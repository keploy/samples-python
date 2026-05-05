#!/usr/bin/env bash
set -Eeuo pipefail

if [ "${DOCCANO_SKIP_BOOTSTRAP:-0}" = "1" ]; then
    echo "Making staticfiles"
    if [ ! -d staticfiles ] || ! find staticfiles -mindepth 1 -print -quit | grep -q .; then
        echo "Executing collectstatic"
        python manage.py collectstatic --noinput
    fi

    echo "Starting django without bootstrap"
    exec gunicorn \
        "--bind=${HOST:-0.0.0.0}:${PORT:-8000}" \
        "--workers=${WORKERS:-1}" \
        --timeout=300 \
        --capture-output \
        --log-level info \
        config.wsgi
fi

exec /opt/bin/prod-django.sh "$@"
