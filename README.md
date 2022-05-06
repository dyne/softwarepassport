# quickstart
docker build -t ipr . && docker run -p 8000:8000 ipr

or

poetry run celery -A ipr.app.celery flower -P threads --loglevel=info
redis-server
poetry run start


# links
https://wiki.debian.org/CopyrightReviewTools

# tests
poetry run pytest
