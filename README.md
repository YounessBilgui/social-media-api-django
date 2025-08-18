# Social Media API (Django + DRF + JWT)

Production-ready minimal social media REST API (posts, comments, likes, follows) built with:
- Python 3.12
- Django 5
- Django REST Framework
- SimpleJWT
- drf-nested-routers
- drf-spectacular (OpenAPI)
- django-cors-headers

## Features
- JWT auth (access 30m / refresh 7d)
- User registration
- Posts CRUD (owner-only edits)
- Comments nested under posts
- Likes (idempotent like/unlike)
- Follows with feed (self + followed posts)
- OpenAPI schema + Swagger UI
- Seed command generating sample data
- Docker + Postgres or local SQLite
- Pre-commit hooks (black, isort, flake8)

## Endpoints (base: /api/)
Auth:
- POST /api/auth/register/
- POST /api/auth/token/
- POST /api/auth/token/refresh/

Users:
- GET /api/users/
- GET /api/users/{id}/
- POST /api/users/{id}/follow/
- DELETE /api/users/{id}/follow/

Posts:
- GET /api/posts/
- POST /api/posts/ (auth)
- GET /api/posts/{id}/
- PATCH/PUT /api/posts/{id}/ (owner)
- DELETE /api/posts/{id}/ (owner)
- POST /api/posts/{id}/like/
- POST or DELETE /api/posts/{id}/unlike/
- GET /api/posts/feed/ (auth) - paginated

Comments (nested):
- GET /api/posts/{post_id}/comments/
- POST /api/posts/{post_id}/comments/ (auth)
- GET /api/posts/{post_id}/comments/{id}/
- PATCH /api/posts/{post_id}/comments/{id}/ (owner)
- DELETE /api/posts/{post_id}/comments/{id}/ (owner)

Schema / Docs:
- GET /api/schema/
- GET /api/docs/

## Quick Start (SQLite)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # adjust if needed
python manage.py migrate
python manage.py runserver
```

Visit: http://127.0.0.1:8000/api/docs/

## Makefile Shortcuts
```bash
make install
make migrate
make run
make seed
make test
make fmt
make lint
```

## JWT Examples
Register:
```bash
curl -X POST http://localhost:8000/api/auth/register/ -H "Content-Type: application/json" -d '{"username":"demo","password":"password123"}'
```

Obtain tokens:
```bash
curl -X POST http://localhost:8000/api/auth/token/ -H "Content-Type: application/json" -d '{"username":"demo","password":"password123"}'
```

Use access token:
```bash
curl -H "Authorization: Bearer <ACCESS>" http://localhost:8000/api/posts/
```

## Feed
```bash
curl -H "Authorization: Bearer <ACCESS>" http://localhost:8000/api/posts/feed/
```

## Seeding Demo Data
```bash
make seed
```
Creates users (alice, bob, charlie, diana, eve) with password `password123`.

## Docker (Postgres)
Create `.env` (edit DB_* if desired):
```bash
cp .env.example .env
```
Run:
```bash
docker compose up --build
```
App: http://localhost:8000/api/docs/

## Switching to Postgres (locally without Docker)
Export env vars or edit `.env` with DB_NAME etc. Run migrations again.

## Tests
```bash
make test
```

## OpenAPI
- Schema JSON: `/api/schema/`
- Swagger UI: `/api/docs/`

## CORS
- Dev: wide open (CORS_ALLOW_ALL=1)
- Production: set `CORS_ALLOW_ALL=0` and define `ALLOWED_HOSTS` & `CORS_ALLOWED_ORIGINS`.

## Acceptance Criteria Checklist
- manage.py check passes
- tests cover auth, posts, comments, likes, follows, feed
- seed command populates demo data
- CRUD with proper permissions
- Idempotent like/unlike + follow/unfollow
- Feed returns followed + self posts
- OpenAPI schema + Swagger
- CORS enabled in dev

## Production Notes
- Set a strong `DJANGO_SECRET_KEY`
- Disable DEBUG
- Configure ALLOWED_HOSTS
- Add TLS termination (reverse proxy)
- Use persistent Postgres volume & proper backup

Enjoy building on top!
