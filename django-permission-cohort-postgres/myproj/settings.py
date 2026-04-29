"""
Minimal Django settings for the django-permission-cohort-postgres
e2e lane (keploy/integrations).

The app exists only to exercise the ContentType permission-lookup
shape that surfaced the postgres-v3 lifetime-gate bug fixed in this
PR. It is intentionally as small as possible: no admin, no static
files, no DRF, no migrations beyond the contenttypes/auth defaults
Django ships out of the box. Anything that doesn't help reproduce
the recorder→lax-promotion→session-fallback path is omitted.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "ci-only-not-secret"
DEBUG = False
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # contenttypes is the load-bearing piece — every request to the
    # /lookup/ view fires SELECT django_content_type WHERE app_label=$1
    # AND model=$2, the exact query the lifetime-gate bug surfaces on.
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # myproj.apps.MyProjConfig spawns a background ContentType-lookup
    # thread when BACKGROUND_LOOKUPS=1 — the keploy/integrations e2e
    # lane uses this to drive DB activity *outside* the HTTP request
    # path, so the recording captures session-pool-bound invocations
    # the lifetime-gate fix unblocks. Off by default; ad-hoc local
    # use of this sample doesn't need it.
    "myproj.apps.MyProjConfig",
]

MIDDLEWARE = []

ROOT_URLCONF = "myproj.urls"

TEMPLATES = []

WSGI_APPLICATION = "myproj.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "djpcohort"),
        "USER": os.environ.get("DB_USER", "djpcohort"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "djpcohort"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        # CONN_MAX_AGE=0 (default) means a fresh connection per request,
        # which makes Django redo any first-connect work each time. We
        # keep that default so the per-request DB call sequence is
        # deterministic across record/replay.
        "OPTIONS": {
            # Skip libpq's SSLRequest preamble. The compose stack runs
            # cleartext postgres; without sslmode=disable, psycopg2
            # sends the SSLRequest byte sequence and waits for an 'S'
            # or 'N' response. Postgres replies with 'R' (auth
            # request, skipping SSL negotiation entirely), keploy's
            # v3 recorder/proxy logs this as "unexpected SSL
            # response", and on the *first* fresh connection at
            # replay time the proxy stalls waiting for an SSL
            # handshake the server isn't going to complete — every
            # first request to a new endpoint then hangs until the
            # client-side timeout fires. Setting sslmode=disable
            # makes psycopg2 skip the preamble entirely so every
            # request flows on the clean cleartext path the proxy
            # already handles.
            "sslmode": "disable",
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USE_TZ = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": "INFO"},
    },
}
