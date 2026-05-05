#!/usr/bin/env bash
#
# Minimum-reproducer traffic for the keploy postgres-v3 simple-Query
# bind regression on doccano. Two subcommands:
#
#   bootstrap        — log in as admin, replace the random
#                      authtoken_token row with a fixed token so
#                      record-time and replay-time API calls share
#                      the same Authorization header. Runs once
#                      against the DOCCANO_SKIP_BOOTSTRAP=0 launch.
#   record-traffic   — drive the actual recording: POST a polymorphic
#                      project, GET it back twice, PATCH it, plus a
#                      couple of dependent reads. The GET / PATCH
#                      responses are what diverge under the bug.
#
# Inputs (all overrideable, defaults chosen to match the
# docker-compose.yml in this directory):
#
#   DOCCANO_APP_PORT       host-side port the backend is exposed on
#   DOCCANO_ADMIN_USER     admin login (set on first boot)
#   DOCCANO_ADMIN_PASSWORD admin password
#   DOCCANO_FIXED_TOKEN    deterministic auth token to install
#   DOCCANO_DB_CONTAINER   postgres container name (for psql)
#   DOCCANO_PHASE          a label spliced into the project name so
#                          record/replay phase logs are
#                          distinguishable; safe-to-omit for local
#                          runs.
set -Eeuo pipefail

DOCCANO_APP_PORT="${DOCCANO_APP_PORT:-18080}"
DOCCANO_ADMIN_USER="${DOCCANO_ADMIN_USER:-admin}"
DOCCANO_ADMIN_PASSWORD="${DOCCANO_ADMIN_PASSWORD:-password}"
DOCCANO_FIXED_TOKEN="${DOCCANO_FIXED_TOKEN:-ac38262065f0ae1476b6a707d9d697a101764a6b}"
DOCCANO_DB_CONTAINER="${DOCCANO_DB_CONTAINER:-doccano_db}"
DOCCANO_BACKEND_CONTAINER="${DOCCANO_BACKEND_CONTAINER:-doccano_backend}"
DOCCANO_PHASE="${DOCCANO_PHASE:-local}"

# Optional per-call audit log written by record-traffic. When set,
# each curl below appends "<METHOD> <URL>" so a downstream caller
# can compute coverage WITHOUT a keploy recording in the picture.
# This is what the standalone GitHub Actions workflow consumes
# (lane scripts use the keploy/test-set-*/tests/*.yaml tree
# instead). When unset / empty: silent no-op, no extra disk writes.
DOCCANO_FIRED_ROUTES_FILE="${DOCCANO_FIRED_ROUTES_FILE:-}"

# log_fired — append "<METHOD> <URL>" to the audit log if enabled.
# Cheap (one printf, no fork) so we can inline it before each curl
# in doccano_record_traffic without bloating the function.
log_fired() {
    [ -z "$DOCCANO_FIRED_ROUTES_FILE" ] && return 0
    printf '%s %s\n' "$1" "$2" >>"$DOCCANO_FIRED_ROUTES_FILE"
}

base="http://127.0.0.1:${DOCCANO_APP_PORT}"
h_token="Authorization: Token ${DOCCANO_FIXED_TOKEN}"
h_json='Content-Type: application/json'

# Login + fixed-token install. Deterministic auth header is what lets
# the recorded HTTP test cases match at replay — without it, every
# replay run would carry a fresh random token in the headers and the
# matcher would diff on the Authorization line.
# doccano_wait_for_fixed_token — poll /v1/me with the deterministic
# Authorization header until the backend returns 200 with the
# admin user's username. Used as a backend-readiness gate, both at
# the end of bootstrap (proves the token install took effect) and
# at the start of record-traffic (proves the second-stage
# skip-bootstrap compose has finished gunicorn boot before we
# fire any test traffic). Distinct from a plain port-open check —
# this gate doesn't return until the auth+DB+Django stack is
# actually serving.
doccano_wait_for_fixed_token() {
    local timeout=${1:-180}
    local start_ts code
    start_ts=$(date +%s)
    while true; do
        code=$(curl -sS -o /tmp/doccano-me.json -w '%{http_code}' \
            -H "$h_token" "${base}/v1/me" 2>/dev/null || echo "")
        if [ "$code" = "200" ] && jq -e ".username == \"${DOCCANO_ADMIN_USER}\"" /tmp/doccano-me.json >/dev/null 2>&1; then
            return 0
        fi
        if [ $(( $(date +%s) - start_ts )) -ge "$timeout" ]; then
            echo "doccano_wait_for_fixed_token: timed out waiting for /v1/me to return 200 (last code: ${code:-<empty>})" >&2
            cat /tmp/doccano-me.json >&2 || true
            return 1
        fi
        sleep 2
    done
}

doccano_bootstrap_token() {
    local timeout=${1:-180}
    local start_ts
    start_ts=$(date +%s)

    while true; do
        local code
        code=$(curl -sS -o /tmp/doccano-login.json -w '%{http_code}' \
            -H 'Content-Type: application/json' \
            -X POST "${base}/v1/auth/login/" \
            -d "{\"username\":\"${DOCCANO_ADMIN_USER}\",\"password\":\"${DOCCANO_ADMIN_PASSWORD}\"}" || true)
        if [ "$code" = "200" ] && jq -e '.key' /tmp/doccano-login.json >/dev/null 2>&1; then
            break
        fi
        if [ $(( $(date +%s) - start_ts )) -ge "$timeout" ]; then
            echo "Timed out waiting for doccano login (last code: ${code})" >&2
            cat /tmp/doccano-login.json >&2 || true
            return 1
        fi
        sleep 2
    done

    docker exec -i "$DOCCANO_DB_CONTAINER" psql -U doccano -d doccano -v ON_ERROR_STOP=1 <<SQL
UPDATE authtoken_token
SET key='${DOCCANO_FIXED_TOKEN}'
WHERE user_id=(SELECT id FROM auth_user WHERE username='${DOCCANO_ADMIN_USER}');
SQL

    # Confirm the fixed token is live before returning.
    doccano_wait_for_fixed_token "$timeout"
}

# Record traffic: hits exactly the endpoints whose responses
# diverge under the bug, plus the dependent reads needed to make the
# polymorphic resolver fire its multi-bind django_content_type
# lookups (the actual root cause we're falsifying).
doccano_record_traffic() {
    local project_resp project_id
    local label_resp label_id
    local example_resp example_id
    local p

    # Wait for the backend to actually be SERVING (not just
    # port-open). Lanes typically wait_for_port before invoking
    # this function, but a TCP-open backend could still be
    # gunicorn-booting and 5xx every API call. doccano_wait_for_fixed_token
    # polls /v1/me with the deterministic auth header until it
    # returns 200, which is the strongest single-call readiness
    # signal: it proves gunicorn is past boot, the auth backend
    # is wired, the named-volume token is loaded, and the DB is
    # responsive. Without this gate, the very first POST below
    # (curl -fsS, no `|| true`) fails with a 5xx, set -e kills
    # the script, the lane's compat_run_record_phase sees a
    # zero-second "traffic done", SIGINTs keploy ~3s after, and
    # the recording captures nothing.
    doccano_wait_for_fixed_token 240 >/dev/null

    # Worker-cache warmup. The sample defaults to one gunicorn worker
    # for deterministic keploy replay, but DOCCANO_WORKERS can raise
    # that count for local experiments. Each worker keeps its own
    # per-process Django ContentType cache and populates it lazily on
    # the first polymorphic-resolver query that worker handles.
    # Recording lanes that terminate with SIGINT (rather than waiting
    # on a long --record-timer) need every worker's cache warmed before
    # the explicit test traffic fires — otherwise cold workers fire
    # their own django_content_type lookups at replay-time, find empty
    # perTest cohorts, and the dependent endpoints return HTTP 500.
    #
    # The fixed 16 calls are gunicorn-dispatch-jitter safe for the
    # previous 4-worker default; /v1/me is the cheapest authenticated
    # endpoint and exercises the same auth-token + ContentType chain
    # as real test calls.
    local warm_idx
    for warm_idx in $(seq 1 16); do
        curl -sS -H "$h_token" "$base/v1/me" >/dev/null 2>&1 || true
    done
    log_fired GET "$base/v1/me"

    log_fired GET "$base/v1/users"
    curl -sS -H "$h_token" "$base/v1/users" >/dev/null || true
    log_fired GET "$base/v1/health/"
    curl -sS "$base/v1/health/" >/dev/null || true

    # POST a polymorphic project. resourcetype="TextClassificationProject"
    # is the polymorphic discriminator that django-rest-polymorphic
    # uses to instantiate the right subclass; the bug shows up at
    # the GET / PATCH side, not on this POST (the in-memory subclass
    # instance shapes the response without consulting the DB).
    log_fired POST "$base/v1/projects"
    project_resp=$(curl -fsS -H "$h_token" -H "$h_json" -X POST "$base/v1/projects" \
        -d "{\"name\":\"keploy-${DOCCANO_PHASE}-project\",\"project_type\":\"DocumentClassification\",\"description\":\"sample project\",\"guideline\":\"label the text\",\"resourcetype\":\"TextClassificationProject\"}")
    project_id=$(printf '%s' "$project_resp" | jq -r '.id')
    [ -n "$project_id" ] && [ "$project_id" != "null" ]

    p="$base/v1/projects/${project_id}"

    # The reads that fail under the bug (GET list / GET single /
    # PATCH single all return resourcetype="Project" instead of
    # "TextClassificationProject" because the polymorphic queryset
    # can't resolve the subclass without working bind-discrimination
    # on django_content_type).
    log_fired GET "$base/v1/projects"
    curl -sS -H "$h_token" "$base/v1/projects" >/dev/null || true
    log_fired GET "$p"
    curl -sS -H "$h_token" "$p" >/dev/null || true
    log_fired PATCH "$p"
    curl -sS -H "$h_token" -H "$h_json" -X PATCH "$p" \
        -d '{"description":"updated by sample"}' >/dev/null || true

    # Dependent reads — exercise the polymorphic resolver on the
    # nested resources so the cohort surfaces multiple variants of
    # the django_content_type lookup at record time. Without these,
    # the recording wouldn't capture the multi-bind shape and the
    # falsifying half of the matrix wouldn't have anything to fail
    # on.
    log_fired GET "$p/my-role"
    curl -sS -H "$h_token" "$p/my-role" >/dev/null || true
    log_fired GET "$p/members"
    curl -sS -H "$h_token" "$p/members" >/dev/null || true

    log_fired POST "$p/category-types"
    label_resp=$(curl -sS -H "$h_token" -H "$h_json" -X POST "$p/category-types" \
        -d '{"text":"positive","background_color":"#00ff00","text_color":"#ffffff"}' 2>/dev/null || true)
    label_id=$(jq -r '.id // empty' <<<"$label_resp" 2>/dev/null || true)
    log_fired GET "$p/category-types"
    curl -sS -H "$h_token" "$p/category-types" >/dev/null || true

    log_fired POST "$p/examples"
    example_resp=$(curl -fsS -H "$h_token" -H "$h_json" -X POST "$p/examples" \
        -d '{"text":"Keploy CI sample text","meta":{"source":"sample"}}')
    example_id=$(jq -r '.id' <<<"$example_resp")
    if [ -n "$example_id" ] && [ "$example_id" != "null" ]; then
        log_fired GET "$p/examples/${example_id}"
        curl -sS -H "$h_token" "$p/examples/${example_id}" >/dev/null || true
        if [ -n "$label_id" ]; then
            log_fired POST "$p/examples/${example_id}/categories"
            curl -sS -H "$h_token" -H "$h_json" -X POST "$p/examples/${example_id}/categories" \
                -d "{\"label\":${label_id}}" >/dev/null || true
        fi
    fi

    # Metrics endpoints — additional polymorphic queries.
    log_fired GET "$p/metrics/progress"
    curl -sS -H "$h_token" "$p/metrics/progress" >/dev/null || true
    log_fired GET "$p/metrics/member-progress"
    curl -sS -H "$h_token" "$p/metrics/member-progress" >/dev/null || true
}

# doccano_report_coverage (real Python line coverage via coverage.py).
#
# Requires the docker-compose.coverage.yml overlay — the base compose
# is uninstrumented so keploy CI lanes (enterprise, integrations) pay
# zero overhead. When called from a base-compose run the function
# detects the missing data and exits 0 cleanly so `flow.sh coverage
# || true` informational hooks don't break.
#
# Mechanics:
#   - The coverage overlay's Dockerfile.coverage installs coverage.py
#     and a `coverage_subprocess.pth` so each gunicorn worker auto-
#     starts coverage.process_startup().
#   - .coveragerc has parallel = true → per-worker .coverage.<pid>
#     files in /coverage (volume-mounted from ./coverage on host).
#   - This function shells into the running backend container,
#     combines the per-worker files in place, and emits the line %
#     in the same `Covered N/M (XX.X%)` shape the helper script's
#     regex expects.
doccano_report_coverage() {
    local backend="${DOCCANO_BACKEND_CONTAINER:-doccano_backend}"
    local data_dir="${DOCCANO_COVERAGE_DATA_DIR:-/coverage}"
    local report_file="${COVERAGE_REPORT_FILE:-coverage_report.txt}"

    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${backend}$"; then
        echo "INFO: ${backend} not running — coverage report skipped"
        : >"$report_file"
        return 0
    fi

    local data_count
    data_count=$(docker exec "$backend" sh -c "ls -1 ${data_dir}/.coverage.* 2>/dev/null | wc -l" 2>/dev/null | tr -d ' \r\n')
    if [ "${data_count:-0}" -eq 0 ]; then
        echo "INFO: no coverage data at ${data_dir}/.coverage.* in ${backend} — base image is uninstrumented (apply docker-compose.coverage.yml overlay to enable)"
        : >"$report_file"
        return 0
    fi

    # Combine in-place; -a appends repeated runs (re-trigger safe).
    docker exec "$backend" sh -c "cd /backend && coverage combine -a ${data_dir}/.coverage.* >/dev/null 2>&1" || true

    # Pull the integer % via --format=total (newer coverage.py emits
    # just the number) plus the textual TOTAL line for the artefact.
    local pct lines covered missed
    pct=$(docker exec "$backend" sh -c "cd /backend && coverage report --rcfile=/backend/.coveragerc --format=total 2>/dev/null" | tr -d ' \r\n')
    if [ -z "$pct" ]; then
        echo "ERROR: coverage report --format=total returned empty"
        docker exec "$backend" sh -c "cd /backend && coverage report --rcfile=/backend/.coveragerc 2>&1 | tail -10" >&2 || true
        return 1
    fi

    # Pull statements/missed off the TOTAL row of the textual report.
    read -r lines missed < <(docker exec "$backend" sh -c "cd /backend && coverage report --rcfile=/backend/.coveragerc 2>/dev/null | awk '/^TOTAL/{print \$2, \$3}'" | tr -d '\r')
    covered=$(( ${lines:-0} - ${missed:-0} ))

    {
        echo "================ doccano line coverage (Python coverage.py) ================"
        docker exec "$backend" sh -c "cd /backend && coverage report --rcfile=/backend/.coveragerc 2>/dev/null | tail -15"
        echo ""
        printf 'Covered %s/%s (%s.0%%)\n' "${covered}" "${lines:-0}" "${pct}"
        echo "============================================================================"
    } | tee "$report_file"
}


case "${1:-}" in
    bootstrap)
        doccano_bootstrap_token "${2:-180}"
        ;;
    record-traffic)
        doccano_record_traffic
        ;;
    coverage)
        # Reads coverage.py data from the running backend container
        # (requires the docker-compose.coverage.yml overlay; exits 0
        # cleanly if the base image is uninstrumented).
        doccano_report_coverage
        ;;
    *)
        cat >&2 <<EOF
usage: $0 {bootstrap|record-traffic|coverage}

  bootstrap      log in as admin and install the deterministic auth
                 token (idempotent; safe to re-run against a populated DB)
  record-traffic drive the API: warmup hammer + project create + reads
                 + label + example + categories + metrics. Fire-and-forget;
                 keploy is the assertion layer at replay
  coverage       compute Python line coverage (coverage.py) of the
                 backend code that the just-finished traffic loop
                 exercised; requires docker-compose.coverage.yml
                 overlay. No-op when run against the base image.
EOF
        exit 2
        ;;
esac
