FROM python:3.10-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install poetry
RUN poetry config virtualenvs.create false


COPY pyproject.toml poetry.lock /usr/src/app/
RUN poetry install --no-root

COPY . .

RUN poetry install

ENV PYTHONPATH=/usr/src/app
