from django.contrib import admin
from .models import Post, Comment, Like, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short_body", "created_at", "likes_count")
    search_fields = ("body", "author__username")
    list_select_related = ("author",)

    def short_body(self, obj):
        return (obj.body[:50] + "...") if len(obj.body) > 50 else obj.body

    def likes_count(self, obj):
        return obj.likes.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post_id", "short_body", "created_at")
    search_fields = ("body", "author__username")
    list_select_related = ("author", "post")

    def short_body(self, obj):
        return (obj.body[:40] + "...") if len(obj.body) > 40 else obj.body


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_select_related = ("user", "post")
    search_fields = ("user__username",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    list_select_related = ("follower", "following")
    search_fields = ("follower__username", "following__username")
