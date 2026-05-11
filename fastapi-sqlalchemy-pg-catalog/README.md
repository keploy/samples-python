# fastapi-sqlalchemy-pg-catalog

Minimal FastAPI + SQLAlchemy 2.x + psycopg2 + Postgres 13 sample that
reproduces the Postgres v3 dispatcher's simple-query `ClassCatalog`
asymmetry (keploy/integrations#193).

## What the bug looks like

At app boot, SQLAlchemy's `Base.metadata.create_all(engine)` issues a
`pg_catalog.pg_class` probe per declared table to decide whether to
skip `CREATE TABLE`. With psycopg2 + parameter-less SQL the probe
goes through the **simple-query** protocol path.

In `pkg/postgres/v3/replayer/dispatcher/dispatcher.go`:

* The **extended-query** path (`runEngineForPortal`, `case
  match.ClassCatalog`) consults the recorded transactional mock first
  and only falls back to the synthetic `Engines.Catalog.Execute` on
  miss.
* The **simple-query** path (`dispatchBySQLHash`, `case
  match.ClassCatalog`) goes straight to the synthetic engine — even
  though a recorded `type: query` mock with `class: CATALOG` and the
  correct rows is sitting in `mocks.yaml`.

With no `type: catalog` snapshot present, the synthetic engine
answers `rows: 0, cc: "SELECT 0"`. SQLAlchemy reads zero rows as
"table missing", issues `CREATE TABLE project ...`, and the
transactional engine misses (because the recording never captured a
CREATE TABLE — at record time the table already existed). The app
worker dies with `psycopg2.DatabaseError: keploy-pg-v3: no recorded
invocation matched`, every HTTP testcase that follows fails with
connection-reset.

## Reproducing locally

```bash
cd fastapi-sqlalchemy-pg-catalog
docker compose build

# Baseline (no keploy) — should pass
docker compose up -d
bash flow.sh
docker compose down -v

# Record
( bash flow.sh > flow-record.log 2>&1 ) &
sudo -E keploy record \
  -c "docker compose -f docker-compose.yml up" \
  --container-name pg-catalog-repro-app \
  --cmd-type docker-compose \
  --record-timer 60s

# Replay (pre-fix: FAILS with "no recorded invocation matched" on CREATE TABLE)
sudo -E keploy test \
  -c "docker compose -f docker-compose.yml up" \
  --container-name pg-catalog-repro-app \
  --cmd-type docker-compose \
  --apiTimeout 120 --delay 15 --disableMockUpload
```

## Layout

| File                        | Purpose                                                                   |
|-----------------------------|---------------------------------------------------------------------------|
| `app/main.py`               | FastAPI app with one declarative `Project` model + lifespan create_all   |
| `app/Dockerfile`            | Python 3.12-slim + requirements                                           |
| `app/requirements.txt`      | fastapi, uvicorn, sqlalchemy 2.0.36, psycopg2-binary 2.9.10               |
| `docker-compose.yml`        | postgres:13.22-alpine + app, app published at host port 8123             |
| `init.sql`                  | Pre-creates the `project` table so record-time create_all is a no-op      |
| `flow.sh`                   | Drives `GET /health` and `GET /projects` against the app                  |

## Compose env knobs

Set these to isolate concurrent runs (the CI lane drives a 3-cell
matrix on one Docker daemon and overrides each):

| Env var          | Default                 | Purpose                                  |
|------------------|-------------------------|------------------------------------------|
| `APP_CONTAINER`  | `pg-catalog-repro-app`  | App container name (keploy `--container-name`) |
| `DB_CONTAINER`   | `pg-catalog-repro-db`   | Postgres container name                  |
| `APP_HOST_PORT`  | `8123`                  | Host-side port mapped to app's 8000      |
| `COMPOSE_NET`    | `reprnet`               | Docker network name                      |

## Used by

* `keploy/integrations` Woodpecker lane
  `.woodpecker/sqlalchemy-pg-catalog-postgres.yml`
