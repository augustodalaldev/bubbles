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

## Demo environment (sample data)
A separate database (`bubbles_teste`, never the development one) filled with pet communities:
```bash
make demo             # creates the DB if needed, migrates, fills it, serves the backend on :8001
make demo-frontend    # second terminal: Vite pointed at the demo backend (VITE_API_TARGET)
make demo-reset       # drop and recreate the demo database from scratch, then `make demo`
make demo-scheduler   # optional: run the periodic jobs against the demo database
```
`make demo` prints the credentials; every account uses the password `DemoPets2026!`:
`admin_demo` (staff, opens `/admin/`), `moderador_demo` (admin of several communities) and a few regular users.
Open http://localhost:5173 after `make demo-frontend`.

What it creates (all through the application's services, so rules, counters and the soap ledger are real):
users with avatars, follows, communities with photos/banners, memberships and roles (leader, admins, a silenced
and a banned member), posts with cat/dog photos, threaded comments, supports, bubblepops (active and expired ones for
the cleanup job), letters and replies, reports (some reviewed, with audit entries), the customization catalog,
purchases by users and by communities (community wallets are funded), and soap balances to found communities.
It also shows the administration states and every customization option: a suspended account
(`suspenso_demo`), a banned one (`banido_demo`, whose login explains the ban), a deleted account (its posts stay as
"Conta excluída"), a suspended, a banned and a deleted community, offline-drawn wallpapers (four variations, one tiled),
three accent colors, two profile sections, extra badges (up to three per profile, one granted by staff) and a banner
for every community. Sign in as `admin_demo` and open `/moderacao` to see them.
Dates are spread over the last 30 days. Photos come from The Cat API and Dog CEO (free, no key), are downloaded once to
`backend/.demo_cache/` (git-ignored) and reused; offline it uses the cache or skips images with a warning.
Photos are stored through the normal upload fields in `backend/media/`.

> Never run `pytest` with `DJANGO_SETTINGS_MODULE` pointing at the demo settings: the tests would use the demo's real
> `backend/media/`. `make test` uses the test settings (a temporary media folder).

Run it directly with `DJANGO_SETTINGS_MODULE=config.settings.demo uv run python manage.py seed_demo` (from `backend/`):
`--seed 42`, `--users 12`, `--communities 6` (max 8), `--posts-per-user 3`, `--comments-per-post 3`,
`--expired-bubblepops 2`, `--days 30`, `--images 12` (photos cached per species), `--no-images`, `--no-download`.
Running it again adds nothing (same seed, same choices). `--reset` deletes only what the seed created (tracked in
`backend/.demo_cache/seed_manifest.json`), including its media files and the ledger rows of the accounts it made,
and keeps anything you created by hand. The command refuses to run outside `config.settings.demo`, with `DEBUG` off, or
on any database other than the demo one.

## Frontend URLs
| URL | Screen |
|---|---|
| `/` · `/?q=term` | Feed · search |
| `/login` · `/register` | Authentication (`?next=/path` returns to the page you wanted) |
| `/u/:username` · `/u/:username/followers` · `/u/:username/following` | Profile (your own too) · follower and following lists |
| `/conta` | Your account: edit profile, change password/e-mail, delete account |
| `/communities` · `/c/:commname` · `/c/:commname/configuracoes` | Community hub · community · its settings (edit, transfer leadership, delete) |
| `/store` | Customization store (frames, themes, badges, name color, wallpapers, accent colors, profile section) |
| `/letters` · `/letters/:id` · `/letters?to=username` | Mailbox · a letter · composer addressed to someone |
| `/moderacao` | Staff only: suspend, ban and restore users and communities; audit history |
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
