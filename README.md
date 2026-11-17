# Bubbles

A community-driven social network built around bubbles and soap.

Backend: Django 5.2 + DRF + PostgreSQL (`backend/`, Python 3.12+, managed with `uv`).
Frontend: React + TypeScript + Vite + Tailwind (`frontend/`).

## Run it
```bash
cp .env.example .env      # then set DJANGO_SECRET_KEY
make up                   # PostgreSQL via Docker
cd backend && uv sync && uv run python manage.py migrate && cd ..
make run                  # API at http://localhost:8000/api/docs/

cd frontend && npm install && cd ..
make frontend-dev         # app at http://localhost:5173 (proxies /api and /media to :8000)
```

Create a staff user with `cd backend && uv run python manage.py createsuperuser` to use the Django Admin
(`/admin/`), where the catalog of customization items and moderation are managed.

## Useful commands
`make test` · `make lint` · `make format` · `make check-migrations` · `make frontend-build`

Periodic jobs (no scheduler is bundled; run them from cron):
`uv run python manage.py distribute_passive_soap` (every few minutes) and
`uv run python manage.py cleanup_expired_bubblepops` (hourly).

## Docs
`docs/REVIEW_PLAN.md` (review and integration plan), `docs/PROGRESS.md`, `docs/DECISIONS.md`,
`docs/REQUIREMENTS_CHANGES.md`, `docs/ER.md`, `docs/frontend/PLAN.md`.
