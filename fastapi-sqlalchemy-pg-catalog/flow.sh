#!/usr/bin/env bash
# Drives traffic during keploy record. Hits both endpoints.
set -uo pipefail

APP_HOST_PORT="${APP_HOST_PORT:-8123}"
APP_URL="${APP_URL:-http://localhost:${APP_HOST_PORT}}"

echo "[flow] waiting for app at $APP_URL ..."
for i in $(seq 1 60); do
  if curl -sf "$APP_URL/health" > /dev/null 2>&1; then
    echo "[flow] app ready after ${i}s"
    break
  fi
  sleep 1
done

echo "[flow] GET /health"
curl -sS "$APP_URL/health" && echo

echo "[flow] GET /projects"
curl -sS "$APP_URL/projects" && echo

echo "[flow] done"
