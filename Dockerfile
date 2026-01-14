FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.2

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with dev

COPY . /app/

RUN poetry run ruff check .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
