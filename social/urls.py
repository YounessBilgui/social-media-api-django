from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import PostViewSet, CommentViewSet, FollowView, RegisterView, UserPublicViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("users", UserPublicViewSet, basename="user")

posts_router = NestedDefaultRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
    path("users/<int:user_id>/follow/", FollowView.as_view(), name="user-follow"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
]
