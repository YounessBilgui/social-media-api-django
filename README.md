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

## Deployment (Optional Task)

If you deploy publicly, share the base URL like:

Examples:
- https://your-api-name.onrender.com/api/
- https://your-api-name.fly.dev/api/
- https://your-api-name.railway.app/api/

Test in an incognito window: https://your-api-base/api/docs/ should load without auth for read-only browsing.

### Required Environment Variables (recommended)
```
DJANGO_SECRET_KEY=<strong-random>
DEBUG=0
ALLOWED_HOSTS=your-domain.com,your-alt-domain.onrender.com
CORS_ALLOW_ALL=0
CORS_ALLOWED_ORIGINS=https://your-frontend.example
DB_NAME=<db>
DB_USER=<user>
DB_PASSWORD=<password>
DB_HOST=<host>
DB_PORT=5432
```

### Render.com (Quick)
1. New + Web Service -> GitHub repo
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3`
4. Add env vars above. (Render sets PORT automatically; gunicorn respects bind.)
5. After deploy: run a one-off shell (Render dashboard) `python manage.py migrate` then (optional) `python manage.py createsuperuser`.

### Railway.app
1. Create project -> Deploy from repo.
2. Add a Postgres plugin; copy its credentials into env vars.
3. Set Start Command as above.
4. Run migrations via Railway shell.

### Fly.io
1. `fly launch` (select Python builder, set internal port 8000).
2. Set secrets: `fly secrets set DJANGO_SECRET_KEY=...` etc.
3. Create a managed Postgres: `fly postgres create` then attach.
4. Deploy: `fly deploy`; run migrations with `fly ssh console -C "python manage.py migrate"`.

### Docker Image (Local Production Sim)
```
docker build -t social-api .
docker run -p 8000:8000 --env-file .env social-api
```

### Static Files
Collected during image build (`collectstatic`) and served via WhiteNoise.

### Health Check
You can use `/api/docs/` (HTML) or `/api/schema/` (JSON) as a basic uptime check; for a JSON lightweight endpoint consider adding `/health/` later.

### Verifying Public URL
1. Open `/api/docs/` with no auth: should load.
2. Execute `POST /api/auth/register/` (if you allow open registration) or use an existing account with `POST /api/auth/token/`.
3. `GET /api/posts/` should return JSON 200.

If 400/500 errors appear, check logs (Render / Railway dashboard) for missing env vars or database errors.

