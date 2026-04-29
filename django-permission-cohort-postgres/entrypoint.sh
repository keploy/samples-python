#!/usr/bin/env bash
# entrypoint.sh — run Django migrations once, then start gunicorn.
#
# The migrations populate django_content_type and the auth_*
# permission tables; without this the /lookup/ endpoint would have
# nothing to find. We migrate inline at container start (rather than
# in a separate init container) so the recorder captures both the
# migration sequence and the runtime queries on the same connection
# pool — keeps the record/replay traffic shape minimal.
set -Eeuo pipefail

echo "[entrypoint] running migrations..."
python /app/manage.py migrate --noinput

echo "[entrypoint] starting gunicorn on :8080..."
exec gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 2 \
  --threads 1 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level info \
  myproj.wsgi:application
