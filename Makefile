.PHONY: up down logs run test lint format check-migrations

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f db

run:
	cd backend && uv run python manage.py runserver

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .

format:
	cd backend && uv run ruff check --fix . && uv run ruff format .

check-migrations:
	cd backend && uv run python manage.py makemigrations --check --dry-run