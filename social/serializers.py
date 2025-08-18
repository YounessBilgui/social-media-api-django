from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Post, Comment, Follow, Like

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "followers_count", "following_count"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )


class CommentSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "post", "body", "created_at", "updated_at"]


class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "body",
            "likes_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(field=serializers.IntegerField())
    def get_likes_count(self, obj) -> int:
        """Return number of likes (annotated or counted)."""
        return int(getattr(obj, "likes_count", None) or obj.likes.count())

    @extend_schema_field(field=serializers.IntegerField())
    def get_comments_count(self, obj) -> int:
        """Return number of comments (annotated or counted)."""
        return int(getattr(obj, "comments_count", None) or obj.comments.count())


class FollowSerializer(serializers.ModelSerializer):
    follower = UserPublicSerializer(read_only=True)
    following = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = fields
