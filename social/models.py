from django.conf import settings
from django.db import models
from django.db.models import Q


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(TimeStamped):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    body = models.TextField(max_length=1000)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Post({self.id}) by {self.author}"


class Comment(TimeStamped):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField(max_length=500)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment({self.id}) on Post({self.post_id})"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_like"),
        ]
        indexes = [
            models.Index(fields=["user", "post"]),
        ]

    def __str__(self):
        return f"Like(user={self.user_id}, post={self.post_id})"


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow"),
            models.CheckConstraint(
                check=~Q(follower=models.F("following")), name="prevent_self_follow"
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "following"]),
        ]

    def __str__(self):
        return f"Follow({self.follower_id}->{self.following_id})"
