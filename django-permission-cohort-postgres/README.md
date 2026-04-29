# django-permission-cohort-postgres

Minimal Django + PostgreSQL sample that reproduces the `django_content_type` permission-lookup pattern. Each request to `/lookup/<app_label>/<model>/` clears Django's in-process `ContentType` cache and forces the SQL:

```sql
SELECT "django_content_type"."id",
       "django_content_type"."app_label",
       "django_content_type"."model"
  FROM "django_content_type"
 WHERE "django_content_type"."app_label" = $1
   AND "django_content_type"."model" = $2
 LIMIT 21
```

That query is what surfaced the postgres v3 session-fallback lifetime-gate bug in [keploy/enterprise#1952](https://github.com/keploy/enterprise/issues/1952). The sample exists so the keploy/integrations e2e lane (`.woodpecker/django-permission-cohort-postgres.yml`) can drive it end-to-end through record + replay.

## Endpoints

| Path | Effect |
|---|---|
| `GET /health/` | `{"status":"ok"}` (used as wait-for-app gate) |
| `GET /lookup/<app_label>/<model>/` | Looks up the matching `ContentType` row, returns `{id, app_label, model}` |

## Run standalone

```bash
docker compose up
curl http://localhost:8080/health/
curl http://localhost:8080/lookup/auth/user/
curl http://localhost:8080/lookup/auth/group/
```

## What it intentionally does NOT have

- No admin
- No DRF / JWT / token auth — the bug shape doesn't need them
- No static files, no templates, no signal handlers, no celery
- No migrations beyond Django's stock contenttypes/auth tables — those are exactly what the lookup hits

The sample is small on purpose so the failing query is the only DB traffic that matters at replay time.

## Why CONN_MAX_AGE=0

Default `CONN_MAX_AGE=0` (a fresh connection per request) makes Django redo any first-connect work on every request. That keeps the per-request DB call sequence deterministic across record/replay — important for a regression sample.
