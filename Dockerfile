FROM python:3.9

WORKDIR /app
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false
COPY . .
RUN poetry install

CMD ["poetry", "run", "start"]
