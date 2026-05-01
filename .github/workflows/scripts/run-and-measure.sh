#!/usr/bin/env bash
#
# run-and-measure.sh — bring doccano up via the sample's compose,
# run flow.sh bootstrap + record-traffic with the per-call audit
# log enabled, run flow.sh coverage, and emit `coverage=PCT`
# onto $GITHUB_OUTPUT for the downstream coverage-gate job.
#
# Called from .github/workflows/doccano-django.yml's
# build-coverage and release-coverage jobs (one per ref under
# comparison). Both jobs source the same script so the
# measurement is identical across refs — any drift in the
# numerator definition would otherwise produce a misleading
# delta.
#
# Inputs (all from the workflow env):
#   DOCCANO_FIRED_ROUTES_FILE   — per-call audit log path; passed
#                                 through to flow.sh so its
#                                 record-traffic loop logs each
#                                 (METHOD, URL) pair, and so its
#                                 coverage subcommand uses that
#                                 file as the standalone
#                                 numerator.
#   DOCCANO_PHASE               — label spliced into the project
#                                 name so build vs. release runs
#                                 don't collide on volume names
#                                 (compose project naming inside
#                                 the GH runner is per-job
#                                 anyway, but DOCCANO_PHASE shows
#                                 up in the test fixtures and
#                                 is useful for diffing logs).
#   GITHUB_OUTPUT               — standard GH Actions sink for
#                                 step outputs.
set -Eeuo pipefail

export DOCCANO_BACKEND_CONTAINER="${DOCCANO_BACKEND_CONTAINER:-doccano_backend}"
export DOCCANO_DB_CONTAINER="${DOCCANO_DB_CONTAINER:-doccano_db}"
export DOCCANO_APP_PORT="${DOCCANO_APP_PORT:-18080}"
export DOCCANO_FIXED_TOKEN="${DOCCANO_FIXED_TOKEN:-ac38262065f0ae1476b6a707d9d697a101764a6b}"
: "${DOCCANO_FIRED_ROUTES_FILE:?DOCCANO_FIRED_ROUTES_FILE must be set by the workflow}"

# Reset audit log for this run; otherwise a prior run's entries
# would inflate the numerator on a re-trigger.
: >"$DOCCANO_FIRED_ROUTES_FILE"

# Stage 1: bring up doccano with bootstrap so the admin user +
# fixed token persist into the named volume.
DOCCANO_SKIP_BOOTSTRAP=0 docker compose up -d

# Wait for the backend to start serving (not just port-open).
# Cold doccano boot runs Django migrations + admin user create,
# which on a GH runner can hit 90-120s.
for i in $(seq 1 120); do
    code=$(curl -sS -o /dev/null -w '%{http_code}' \
        "http://127.0.0.1:${DOCCANO_APP_PORT}/v1/health/" 2>/dev/null || echo "")
    if [ -n "$code" ] && [ "$code" != "000" ]; then break; fi
    sleep 2
done

bash flow.sh bootstrap 240
docker compose down --remove-orphans

# Stage 2: re-launch in skip-bootstrap mode against the populated
# volume — same shape the keploy lanes use.
DOCCANO_SKIP_BOOTSTRAP=1 docker compose up -d

# Drive traffic. flow.sh::doccano_record_traffic gates on
# doccano_wait_for_fixed_token internally, so this won't fire
# curls at a half-booted backend.
bash flow.sh record-traffic

# Coverage report — uses DOCCANO_FIRED_ROUTES_FILE as numerator
# since no keploy/test-set-* tree exists in the standalone case.
COVERAGE_REPORT_FILE="$PWD/coverage_report.txt" bash flow.sh coverage

# Pull the percentage out of the report's `Covered N/M (XX.X%)`
# line. Anchored on the parenthesised form so a future change to
# the report's prose doesn't break the parse.
pct=$(grep -oE '\([0-9]+\.[0-9]+%\)' coverage_report.txt | head -1 | tr -d '()%')
if [ -z "$pct" ]; then
    echo "::error::Could not parse coverage percentage from coverage_report.txt"
    cat coverage_report.txt || true
    exit 1
fi
echo "coverage=${pct}" >>"$GITHUB_OUTPUT"
echo "coverage: ${pct}% (audit log: $DOCCANO_FIRED_ROUTES_FILE)"

docker compose down -v --remove-orphans
