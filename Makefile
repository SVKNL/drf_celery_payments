.PHONY: install run worker migrate makemigrations test test-docker lint typecheck

install:
	poetry install

run:
	poetry run python manage.py runserver 0.0.0.0:8000

worker:
	poetry run celery -A config worker -l info

migrate:
	poetry run python manage.py migrate

makemigrations:
	poetry run python manage.py makemigrations

test:
	poetry run pytest

test-docker:
	docker compose -f docker-compose.yml -f docker-compose.test.yml up -d db redis
	poetry run pytest

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy .
