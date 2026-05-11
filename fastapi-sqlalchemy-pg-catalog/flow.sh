#!/usr/bin/env bash
# Drives traffic during keploy record. Hits both endpoints.
set -Eeuo pipefail

APP_HOST_PORT="${APP_HOST_PORT:-8123}"
APP_URL="${APP_URL:-http://localhost:${APP_HOST_PORT}}"
READY_TIMEOUT_S="${READY_TIMEOUT_S:-60}"

echo "[flow] waiting for app at $APP_URL (ceiling ${READY_TIMEOUT_S}s) ..."
ready=0
for i in $(seq 1 "$READY_TIMEOUT_S"); do
  if curl -fsS --max-time 1 "$APP_URL/health" > /dev/null 2>&1; then
    echo "[flow] app ready after ${i}s"
    ready=1
    break
  fi
  sleep 1
done

if [ "$ready" -ne 1 ]; then
  echo "[flow] ERROR: app never became ready at $APP_URL/health within ${READY_TIMEOUT_S}s" >&2
  exit 1
fi

echo "[flow] GET /health"
curl -fsS "$APP_URL/health"
echo

echo "[flow] GET /projects"
curl -fsS "$APP_URL/projects"
echo

echo "[flow] done"
