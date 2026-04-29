#!/usr/bin/env bash
# entrypoint.sh — start gunicorn.
#
# Migrations are applied by a sibling `migrator` service in
# docker-compose.yml that runs to completion before this container
# starts. Keeping the migration step out of the api container is what
# lets the keploy/integrations record-replay lane stay deterministic:
# Django's `post_migrate` signal bulk-inserts ContentType rows in a
# single simple-query INSERT whose row ordering depends on model-
# registration timing, and capturing that under the keploy proxy
# would make recordings non-replayable across runs.
set -Eeuo pipefail

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
