FROM python:3.10-slim

WORKDIR /app

# Instalăm dependențele sistemului necesare pentru unele librării Python
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Colectăm fișierele statice (pentru designul magazinului)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]