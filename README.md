# DRF Celery Payouts

REST-сервис для заявок на выплату с асинхронной обработкой через Celery.

## Требования

- Python 3.10+
- Poetry
- PostgreSQL
- Redis

## Локальный запуск (Poetry)

1. Установка зависимостей:

```bash
poetry install
```

2. Переменные окружения (пример для Windows PowerShell):

```bash
set DATABASE_URL=postgresql://user:password@localhost:5432/payouts
set CELERY_BROKER_URL=redis://localhost:6379/0
set CELERY_RESULT_BACKEND=redis://localhost:6379/0
set DJANGO_SECRET_KEY=change-me
```

3. Миграции:

```bash
poetry run python manage.py migrate
```

4. Запуск API:

```bash
poetry run python manage.py runserver 0.0.0.0:8000
```

5. Запуск Celery worker:

```bash
poetry run celery -A config worker -l info
```

6. Тесты:

```bash
poetry run pytest
```

7. Линтер:

```bash
poetry run ruff check .
```

8. Проверка типов:

```bash
poetry run mypy .
```

## API

- GET /api/payouts/
- GET /api/payouts/{id}/
- POST /api/payouts/
- PATCH /api/payouts/{id}/
- DELETE /api/payouts/{id}/
- OpenAPI схема: /api/schema/
- Swagger UI: /api/docs/

## Docker

```bash
docker compose up --build
```

Миграции внутри контейнера:

```bash
docker compose exec web python manage.py migrate
```

## Тесты с Docker

По умолчанию тесты ожидают PostgreSQL на `localhost:5433`. Для этого поднимите тестовые сервисы:

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d db redis
poetry run pytest
```

Если нужно использовать другую базу, переопределите `DATABASE_URL`.

Makefile shortcut:

```bash
make test-docker
```

## Команды Makefile

```bash
make run
make worker
make migrate
make test
make lint
make typecheck
```

## Деплой (кратко)

В продакшене сервис обычно запускается так:

- PostgreSQL как основная БД
- Redis как брокер/бэкенд результатов Celery
- Django приложение под Gunicorn
- Отдельные Celery worker процессы
- Reverse proxy (например, Nginx) для TLS и проксирования

Минимальные шаги:

1. Подготовить PostgreSQL и Redis.
2. Собрать образ приложения и выполнить миграции.
3. Запустить Gunicorn с Django-приложением.
4. Запустить Celery worker(ы) с теми же настройками окружения.
5. Настроить Nginx для TLS и маршрутизации.
