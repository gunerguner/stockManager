#!/bin/sh
set -e

if [ -n "${SQLITE_PATH:-}" ]; then
  mkdir -p "$(dirname "${SQLITE_PATH}")"
fi

mkdir -p /var/log/stockmanager/django

if [ "${SQLITE_MUST_EXIST:-true}" = "true" ] && [ ! -f "${SQLITE_PATH:-/app/data/db.sqlite3}" ]; then
  echo "ERROR: SQLITE_MUST_EXIST=true but sqlite file not found: ${SQLITE_PATH:-/app/data/db.sqlite3}" >&2
  exit 1
fi

if [ "${RUN_MIGRATIONS_ON_START:-false}" = "true" ]; then
  echo "Running Django migrations..."
  python manage.py migrate --noinput
else
  echo "Skipping Django migrations on startup (RUN_MIGRATIONS_ON_START=false)."
fi

exec gunicorn stockManager.wsgi:application -c /app/gunicorn.docker.conf.py
