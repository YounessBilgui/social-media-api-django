import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from social.models import Post, Comment, Like, Follow

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data (users, follows, posts, comments, likes)."

    def handle(self, *args, **options):
        usernames = ["alice", "bob", "charlie", "diana", "eve"]
        users = []
        for name in usernames:
            u, created = User.objects.get_or_create(username=name)
            if created:
                u.set_password("password123")
                u.save()
            users.append(u)

        # Follows (avoid self)
        for follower in users:
            others = [u for u in users if u != follower]
            if not others:
                continue
            sample = random.sample(others, k=random.randint(1, min(3, len(others))))
            for target in sample:
                Follow.objects.get_or_create(follower=follower, following=target)

        bodies = [
            "Hello world",
            "Another sunny day",
            "Exploring Django REST",
            "Writing tests is fun",
            "Seeding the database",
            "Random thoughts...",
            "Coffee first",
            "Working on an API",
            "Edge cases matter",
            "Final demo post",
        ]
        posts = []
        for _ in range(random.randint(10, 20)):
            author = random.choice(users)
            body = random.choice(bodies)
            p = Post.objects.create(author=author, body=body)
            posts.append(p)

        # Comments
        for p in posts:
            for _ in range(random.randint(0, 3)):
                Comment.objects.create(
                    author=random.choice(users),
                    post=p,
                    body=f"Comment on post {p.id}",
                )

        # Likes
        for p in posts:
            likers = random.sample(users, k=random.randint(0, len(users)))
            for u in likers:
                Like.objects.get_or_create(user=u, post=p)

        self.stdout.write(self.style.SUCCESS("Seed data created."))
