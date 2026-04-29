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
# --timeout 300: matcher round-trips through the keploy proxy can spike
#   under CI load; gunicorn's default 30s SIGKILLs the worker mid-request
#   and the test that landed on that worker times out client-side. 300s
#   gives the proxy comfortable headroom.
# --workers 4 / --threads 2: enough concurrency that a single slow
#   matcher response doesn't queue subsequent requests behind it.
exec gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --threads 2 \
  --timeout 300 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level info \
  myproj.wsgi:application
