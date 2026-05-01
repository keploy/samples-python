#!/usr/bin/env bash
#
# run-and-measure.sh — bring doccano up under the coverage overlay,
# run flow.sh bootstrap + record-traffic, flush coverage from each
# gunicorn worker, run flow.sh coverage to combine + report, and
# emit `coverage=PCT` onto $GITHUB_OUTPUT for the downstream
# coverage-gate job.
#
# Called from .github/workflows/doccano-django.yml's build-coverage
# and release-coverage jobs (one per ref under comparison). Both
# jobs source the same script so the measurement is identical
# across refs — any drift in the numerator definition would
# otherwise produce a misleading delta.
#
# Coverage isolation contract:
#   * Base `Dockerfile` and `docker-compose.yml` are untouched.
#   * The overlay `Dockerfile.coverage` + `docker-compose.coverage.yml`
#     adds coverage.py + the auto-start .pth file. ONLY this script
#     applies the overlay; the keploy/integrations and
#     keploy/enterprise CI lanes consume the base compose and pay
#     zero coverage-instrumentation cost.
#
# Inputs (from the workflow env):
#   DOCCANO_PHASE     — label spliced into the project name so
#                       build vs release runs don't collide.
#   GITHUB_OUTPUT     — standard GH Actions sink for step outputs.
set -Eeuo pipefail

export DOCCANO_BACKEND_CONTAINER="${DOCCANO_BACKEND_CONTAINER:-doccano_backend}"
export DOCCANO_DB_CONTAINER="${DOCCANO_DB_CONTAINER:-doccano_db}"
export DOCCANO_APP_PORT="${DOCCANO_APP_PORT:-18080}"
export DOCCANO_FIXED_TOKEN="${DOCCANO_FIXED_TOKEN:-ac38262065f0ae1476b6a707d9d697a101764a6b}"

mkdir -p coverage
chmod 777 coverage    # worker UID inside container differs from runner UID
sudo rm -rf coverage/.coverage* 2>/dev/null || rm -rf coverage/.coverage* 2>/dev/null || true

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.coverage.yml)

# Stage 1: bring up doccano with bootstrap so the schema migrations
# and the admin user persist into the named DB volume. The overlay
# image runs gunicorn with coverage.process_startup() auto-armed in
# every forked worker.
DOCCANO_SKIP_BOOTSTRAP=0 "${COMPOSE[@]}" up -d --build

# Wait for the backend to start serving (cold doccano boot runs
# Django migrations + admin user create — on a GH runner this can
# hit 90-120s).
for i in $(seq 1 120); do
    code=$(curl -sS -o /dev/null -w '%{http_code}' \
        "http://127.0.0.1:${DOCCANO_APP_PORT}/v1/health/" 2>/dev/null || echo "")
    if [ -n "$code" ] && [ "$code" != "000" ]; then break; fi
    sleep 2
done

bash flow.sh bootstrap 240
"${COMPOSE[@]}" down --remove-orphans

# Stage 2: re-launch in skip-bootstrap mode against the populated
# volume; same shape the keploy lanes use. The overlay layer is
# preserved across compose-down (only `down -v` would wipe the
# named volume), so coverage tooling is still wired in.
DOCCANO_SKIP_BOOTSTRAP=1 "${COMPOSE[@]}" up -d

# flow.sh::doccano_record_traffic gates on doccano_wait_for_fixed_token
# internally, so this won't fire curls at a half-booted backend.
bash flow.sh record-traffic

# Flush coverage from each gunicorn worker. coverage.py with
# sigterm = true writes the in-flight per-worker .coverage.<pid>
# data file to /coverage on SIGTERM; `compose kill -s SIGTERM`
# delivers it to the container's main process which propagates to
# its workers via gunicorn's graceful shutdown.
"${COMPOSE[@]}" kill -s SIGTERM backend
# coverage.py's sigterm hook is synchronous but the OS-level
# write+fsync needs a moment.
sleep 3

# Bring backend back up so `flow.sh coverage` can docker-exec
# `coverage combine` + `coverage report` inside.
"${COMPOSE[@]}" up -d backend
for i in $(seq 1 60); do
    if docker exec "$DOCCANO_BACKEND_CONTAINER" sh -c 'ls /coverage/.coverage.* >/dev/null 2>&1'; then
        break
    fi
    sleep 1
done

COVERAGE_REPORT_FILE="$PWD/coverage_report.txt" bash flow.sh coverage

# Parse `Covered N/M (XX.X%)` — anchored on the parenthesised form
# so a future report-prose change doesn't break the parse.
pct=$(grep -oE '\([0-9]+\.[0-9]+%\)' coverage_report.txt | head -1 | tr -d '()%')
if [ -z "$pct" ]; then
    echo "::error::Could not parse coverage percentage from coverage_report.txt"
    cat coverage_report.txt || true
    exit 1
fi
echo "coverage=${pct}" >>"$GITHUB_OUTPUT"
echo "coverage: ${pct}% (Python line coverage via coverage.py)"

"${COMPOSE[@]}" down -v --remove-orphans
