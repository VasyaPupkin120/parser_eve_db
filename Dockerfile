FROM python:3.11-slim

RUN python3 -m pip install poetry
RUN poetry config virtualenvs.create false

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
RUN poetry install --no-ansi --no-interaction --no-root

COPY . /code/
