
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt


FROM nginx:alpine AS nginx_builder
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf


FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*


COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


COPY --from=nginx_builder /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

COPY . /app/


RUN mkdir -p /app/static /app/media

EXPOSE 80

CMD \
  python manage.py collectstatic --noinput && \
  (nginx &) && \
  daphne -b 0.0.0.0 -p 8001 SecurityGuard.asgi:application
