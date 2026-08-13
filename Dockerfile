FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*


COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY src/ .

# SECRET_KEY e obligatoriu la import-ul settings.py când DEBUG=False (vezi config/settings.py),
# dar la build time Render nu garantează variabilele de mediu din Environment.
# Colectarea fișierelor statice nu are nevoie de o cheie reală, doar de una prezentă.
RUN SECRET_KEY=build-time-placeholder python manage.py collectstatic --noinput

EXPOSE 8000

# La fiecare pornire: aplică migrațiile, populează catalogul demo (idempotent - sigur de rulat
# de mai multe ori) și pornește gunicorn (server de producție, nu manage.py runserver).
CMD python manage.py migrate --noinput && python manage.py seed_products && gunicorn config.wsgi:application --bind 0.0.0.0:8000