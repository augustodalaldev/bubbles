.PHONY: up down logs run scheduler scheduler-once test lint format check-migrations frontend-dev frontend-build demo demo-db demo-reset demo-frontend demo-scheduler

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

# --------------------------------------------------------------------------------------------
# Demo environment: a separate database (never the development one), filled with sample data.
# --------------------------------------------------------------------------------------------
DEMO_DB ?= bubbles_teste
DEMO_PORT ?= 8001
DEV_DB := $(shell grep -E '^POSTGRES_DB=' .env 2>/dev/null | cut -d= -f2)
DEMO_ENV = DJANGO_SETTINGS_MODULE=config.settings.demo POSTGRES_DB_DEMO=$(DEMO_DB)

# demo-reset drops a database, so refuse anything that could be the development one.
ifneq ($(filter demo demo-db demo-reset demo-scheduler,$(MAKECMDGOALS)),)
ifeq ($(DEMO_DB),$(DEV_DB))
$(error DEMO_DB ($(DEMO_DB)) is the development database (POSTGRES_DB). Pick another name)
endif
ifeq ($(DEMO_DB),postgres)
$(error DEMO_DB cannot be the maintenance database)
endif
endif

demo-db:
	@docker exec bubbles-db sh -c "psql -U \"\$$POSTGRES_USER\" -d postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='$(DEMO_DB)'\" | grep -q 1 || psql -U \"\$$POSTGRES_USER\" -d postgres -c 'CREATE DATABASE $(DEMO_DB)'"

# Create the demo database if needed, migrate, fill it and serve the backend on $(DEMO_PORT).
# Point the frontend at it with: make demo-frontend
demo: demo-db
	cd backend && $(DEMO_ENV) uv run python manage.py migrate -v0
	cd backend && $(DEMO_ENV) uv run python manage.py seed_demo
	@echo "Demo backend: http://127.0.0.1:$(DEMO_PORT)  (frontend: make demo-frontend)"
	cd backend && $(DEMO_ENV) uv run python manage.py runserver 127.0.0.1:$(DEMO_PORT)

# Recreate the demo database from scratch, then run `make demo`.
demo-reset:
	@# First remove what the seed created (including its media files), then drop the database.
	-cd backend && $(DEMO_ENV) uv run python manage.py seed_demo --reset
	@docker exec bubbles-db sh -c "psql -U \"\$$POSTGRES_USER\" -d postgres -c 'DROP DATABASE IF EXISTS $(DEMO_DB) WITH (FORCE)'"
	rm -f backend/.demo_cache/seed_manifest.json
	$(MAKE) demo

demo-frontend:
	cd frontend && VITE_API_TARGET=http://127.0.0.1:$(DEMO_PORT) npm run dev

demo-scheduler:
	cd backend && $(DEMO_ENV) uv run python manage.py run_scheduler

