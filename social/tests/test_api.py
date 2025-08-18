from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class SocialAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")

    def auth_headers(self, username="alice", password="password123"):
        r = self.client.post(
            "/api/auth/token/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        return {"HTTP_AUTHORIZATION": f"Bearer {r.data['access']}"}

    def test_register_and_login(self):
        r = self.client.post(
            "/api/auth/register/",
            {"username": "charlie", "password": "password123"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        r2 = self.client.post(
            "/api/auth/token/",
            {"username": "charlie", "password": "password123"},
            format="json",
        )
        self.assertEqual(r2.status_code, 200)
        self.assertIn("access", r2.data)

    def test_create_post_and_permissions(self):
        headers = self.auth_headers()
        r = self.client.post(
            "/api/posts/", {"body": "Hello world"}, format="json", **headers
        )
        self.assertEqual(r.status_code, 201)
        post_id = r.data["id"]
        # Other user cannot update
        headers_bob = self.auth_headers("bob")
        r2 = self.client.patch(
            f"/api/posts/{post_id}/",
            {"body": "Hacked"},
            format="json",
            **headers_bob,
        )
        self.assertEqual(r2.status_code, 403)
        # Owner can update
        r3 = self.client.patch(
            f"/api/posts/{post_id}/",
            {"body": "Edited"},
            format="json",
            **headers,
        )
        self.assertEqual(r3.status_code, 200)

    def test_like_unlike(self):
        headers = self.auth_headers()
        post = self.client.post(
            "/api/posts/", {"body": "Like me"}, format="json", **headers
        ).data
        pid = post["id"]
        r1 = self.client.post(f"/api/posts/{pid}/like/", **headers)
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.post(f"/api/posts/{pid}/like/", **headers)  # idempotent
        self.assertEqual(r2.status_code, 200)
        r3 = self.client.post(f"/api/posts/{pid}/unlike/", **headers)
        self.assertEqual(r3.status_code, 200)
        r4 = self.client.post(f"/api/posts/{pid}/unlike/", **headers)  # still ok
        self.assertEqual(r4.status_code, 200)

    def test_follow_unfollow_and_feed(self):
        headers_alice = self.auth_headers()
        headers_bob = self.auth_headers("bob")
        # Bob creates a post
        p = self.client.post(
            "/api/posts/", {"body": "Bob's post"}, format="json", **headers_bob
        )
        self.assertEqual(p.status_code, 201)
        # Feed empty before follow
        feed_before = self.client.get("/api/posts/feed/", **headers_alice)
        self.assertEqual(feed_before.status_code, 200)
        self.assertEqual(feed_before.data["count"], 0)
        # Alice follows Bob
        f = self.client.post(f"/api/users/{self.user2.id}/follow/", **headers_alice)
        self.assertIn(f.status_code, [200, 201])
        # Feed now includes Bob's post
        feed_after = self.client.get("/api/posts/feed/", **headers_alice)
        self.assertEqual(feed_after.status_code, 200)
        self.assertEqual(feed_after.data["count"], 1)
        # Unfollow
        unf = self.client.delete(
            f"/api/users/{self.user2.id}/follow/", **headers_alice
        )
        self.assertEqual(unf.status_code, 204)

    def test_comments_crud_and_permissions(self):
        headers = self.auth_headers()
        post = self.client.post(
            "/api/posts/", {"body": "Post with comments"}, format="json", **headers
        ).data
        pid = post["id"]
        c = self.client.post(
            f"/api/posts/{pid}/comments/",
            {"body": "First comment"},
            format="json",
            **headers,
        )
        self.assertEqual(c.status_code, 201)
        cid = c.data["id"]
        # Other user cannot edit
        headers_bob = self.auth_headers("bob")
        r2 = self.client.patch(
            f"/api/posts/{pid}/comments/{cid}/",
            {"body": "Nope"},
            format="json",
            **headers_bob,
        )
        self.assertEqual(r2.status_code, 403)
        # Owner edits
        r3 = self.client.patch(
            f"/api/posts/{pid}/comments/{cid}/",
            {"body": "Updated"},
            format="json",
            **headers,
        )
        self.assertEqual(r3.status_code, 200)

    def test_openapi_available(self):
        r = self.client.get("/api/schema/")
        self.assertEqual(r.status_code, 200)
