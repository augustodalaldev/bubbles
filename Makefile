.PHONY: up down logs run scheduler scheduler-once test lint format check-migrations frontend-dev frontend-build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f db

run:
	cd backend && uv run python manage.py runserver

# Periodic jobs (passive soap, bubblepop cleanup). Works outside Docker; stop with Ctrl+C.
scheduler:
	cd backend && uv run python manage.py run_scheduler

# Run every job once and exit (cron friendly, non-zero on failure).
scheduler-once:
	cd backend && uv run python manage.py run_scheduler --once

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .

format:
	cd backend && uv run ruff check --fix . && uv run ruff format .

check-migrations:
	cd backend && uv run python manage.py makemigrations --check --dry-run