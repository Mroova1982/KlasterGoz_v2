# Klaster GOZ — portal

Portal marketingowy `klastergoz.pl` zarządzany przez Wagtail CMS.

## Stack

- Wagtail 6 / Django 5 / Python 3.12+
- PostgreSQL 16 / Redis 7
- Docker Compose dla dev

## Setup (dev)

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up -d
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Strona: http://localhost:8000
Admin: http://localhost:8000/admin

## Dokumentacja projektu

- Spec: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md`
- Plany: `docs/superpowers/plans/`
