from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Post, Comment, Like, Follow
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    PostSerializer,
    CommentSerializer,
    RegisterSerializer,
    FollowSerializer,
    UserPublicSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserPublicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPublicSerializer
    queryset = (
        User.objects.all()
        .annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        )
        .order_by("id")
    )


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return (
            Post.objects.select_related("author")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        return Response({"detail": "liked" if created else "already liked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated], url_path="unlike")
    def unlike(self, request, pk=None):
        post = self.get_object()
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({"detail": "unliked"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated], url_path="feed")
    def feed(self, request):
        following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
        qs = self.get_queryset().filter(author__in=list(following_ids) + [request.user.id])
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments nested under a post."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    # Base queryset for schema generation; actual filtering in get_queryset
    queryset = Comment.objects.select_related("author", "post")

    def get_queryset(self):  # type: ignore[override]
        return self.queryset.filter(post_id=self.kwargs["post_pk"]).select_related(
            "author", "post"
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs["post_pk"])


@extend_schema_view(
    post=extend_schema(summary="Follow a user", description="Current user follows target user (idempotent)."),
    delete=extend_schema(summary="Unfollow a user", description="Current user unfollows target user (idempotent)."),
)
class FollowView(GenericAPIView):
    """Handle follow/unfollow operations."""

    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer

    def post(self, request, user_id: int):  # type: ignore[override]
        if request.user.id == user_id:
            return Response({"detail": "Cannot follow self."}, status=400)
        target = get_object_or_404(User, pk=user_id)
        obj, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )
        data = self.get_serializer(obj).data
        return Response(
            data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def delete(self, request, user_id: int):  # type: ignore[override]
        Follow.objects.filter(follower=request.user, following_id=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
