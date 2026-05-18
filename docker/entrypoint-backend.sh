#!/bin/sh
set -e

if [ -n "${SQLITE_PATH:-}" ]; then
  mkdir -p "$(dirname "${SQLITE_PATH}")"
fi

mkdir -p /var/log/stockmanager/django

python manage.py migrate --noinput

exec gunicorn stockManager.wsgi:application -c /app/gunicorn.docker.conf.py
