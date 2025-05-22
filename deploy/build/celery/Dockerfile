FROM python:3.11-slim

WORKDIR /code

RUN python3 -m pip install poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
COPY poetry.lock pyproject.toml /code/
RUN poetry install --no-ansi --no-interaction --no-root

COPY . /code/
