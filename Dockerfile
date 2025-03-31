# Étape de construction
FROM python:3.9-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY src .

ENV PATH=/root/.local/bin:$PATH

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=myapp.settings.production \
    PORT=8000

EXPOSE $PORT

RUN python manage.py collectstatic --noinput

CMD gunicorn --bind :$PORT --workers 3 myapp.wsgi:application