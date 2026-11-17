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

## Frontend URLs
| URL | Screen |
|---|---|
| `/` · `/?q=term` | Feed · search |
| `/login` · `/register` | Authentication (`?next=/path` returns to the page you wanted) |
| `/u/:username` | Profile (your own too) |
| `/communities` · `/c/:commname` | Community hub · community |
| `/store` | Customization store |
| `/letters` · `/letters?to=username` | Mailbox · composer addressed to someone |
| `/p/:id` | A single post (shareable link) |
| anything else | 404 page |

Dev: the Vite server already falls back to `index.html` for these paths. Point it at another backend with
`VITE_API_TARGET=http://127.0.0.1:8001 make frontend-dev`.

**Production:** whatever serves `frontend/dist` must answer every non-file path with `index.html`
(the app is a single-page app), otherwise reloading `/c/some_comm` returns the server's 404. nginx:
```nginx
location / { root /var/www/bubbles; try_files $uri /index.html; }
location /api/ { proxy_pass http://127.0.0.1:8000; }
location /media/ { proxy_pass http://127.0.0.1:8000; }
```
`npm run preview` (Vite) already does this fallback.

## Scheduler (passive soap and bubblepop cleanup)
```bash
make scheduler        # keeps running; stop with Ctrl+C (SIGINT/SIGTERM stop it cleanly)
make scheduler-once   # run every job once and exit (non-zero if one failed)
```
`manage.py run_scheduler` is a small in-process loop (no Celery/Redis) and works the same inside or
outside Docker. Intervals:

| Job | Runs | Why |
|---|---|---|
| `distribute_passive_soap` | every `passive_interval_minutes` (5 by default, re-read from the economy settings), aligned to the interval | Payment is idempotent per interval window, so one run per window pays exactly once |
| `cleanup_expired_bubblepops` | every 60 minutes (`--cleanup-interval`) | Expired bubblepops are already hidden when read; the job only frees rows and disk |

Options: `--passive-interval SECONDS`, `--cleanup-interval SECONDS`, `--no-run-on-start`, `--once`.
Every execution is logged (`started` / `finished in Xs -> result` / `FAILED` with traceback); a failing
job is logged and retried on its next run without stopping the scheduler or the other job.
Running two schedulers (or a scheduler plus a manual run) is safe: the jobs take a PostgreSQL advisory
lock, so overlapping runs never pay or delete twice.

Alternative without the loop (cron): `*/5 * * * * cd /path/backend && uv run python manage.py run_scheduler --once`
(passive soap is idempotent per window, so extra runs are harmless).

## Docs
`docs/REVIEW_PLAN.md` (review and integration plan), `docs/PROGRESS.md`, `docs/DECISIONS.md`,
`docs/REQUIREMENTS_CHANGES.md`, `docs/ER.md`, `docs/frontend/PLAN.md`.
