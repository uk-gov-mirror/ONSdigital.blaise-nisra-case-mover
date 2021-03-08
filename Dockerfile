FROM python:3.7

RUN pip install poetry

COPY . .

RUN poetry install

CMD poetry run gunicorn --bind :${PORT:-8080} blaise_nisra_case_mover:app
