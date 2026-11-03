# Bubbles

A community-driven social network built around bubbles and soap.

## Run the backend
```bash
cp .env.example .env      # then set DJANGO_SECRET_KEY
make up                   # PostgreSQL via Docker
cd backend && uv sync
make run                  # http://localhost:8000/api/docs/
```

## Useful commands
`make test` · `make lint` · `make format` · `make check-migrations`