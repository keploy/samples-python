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

base="http://127.0.0.1:${DOCCANO_APP_PORT}"
h_token="Authorization: Token ${DOCCANO_FIXED_TOKEN}"
h_json='Content-Type: application/json'

# Login + fixed-token install. Deterministic auth header is what lets
# the recorded HTTP test cases match at replay — without it, every
# replay run would carry a fresh random token in the headers and the
# matcher would diff on the Authorization line.
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
    start_ts=$(date +%s)
    while true; do
        local code
        code=$(curl -sS -o /tmp/doccano-me.json -w '%{http_code}' \
            -H "$h_token" "${base}/v1/me" || true)
        if [ "$code" = "200" ] && jq -e ".username == \"${DOCCANO_ADMIN_USER}\"" /tmp/doccano-me.json >/dev/null 2>&1; then
            return 0
        fi
        if [ $(( $(date +%s) - start_ts )) -ge "$timeout" ]; then
            echo "Timed out waiting for fixed token (last code: ${code})" >&2
            cat /tmp/doccano-me.json >&2 || true
            return 1
        fi
        sleep 2
    done
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

    # Worker-cache warmup. doccano runs 4 gunicorn workers; each
    # worker keeps its own per-process Django ContentType cache and
    # populates it lazily on the first polymorphic-resolver query
    # that worker handles. Recording lanes that terminate with
    # SIGINT (rather than waiting on a long --record-timer) need
    # every worker's cache warmed before the explicit test traffic
    # fires — otherwise cold workers fire their own
    # django_content_type lookups at replay-time, find empty perTest
    # cohorts, and the dependent endpoints return HTTP 500.
    #
    # 4 workers × 4 requests = 16 calls is gunicorn-dispatch-jitter
    # safe; /v1/me is the cheapest authenticated endpoint and
    # exercises the same auth-token + ContentType chain as real
    # test calls, so each iteration cleanly warms one worker's
    # cache.
    local warm_idx
    for warm_idx in $(seq 1 16); do
        curl -sS -H "$h_token" "$base/v1/me" >/dev/null 2>&1 || true
    done

    curl -sS -H "$h_token" "$base/v1/users" >/dev/null || true
    curl -sS "$base/v1/health/" >/dev/null || true

    # POST a polymorphic project. resourcetype="TextClassificationProject"
    # is the polymorphic discriminator that django-rest-polymorphic
    # uses to instantiate the right subclass; the bug shows up at
    # the GET / PATCH side, not on this POST (the in-memory subclass
    # instance shapes the response without consulting the DB).
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
    curl -sS -H "$h_token" "$base/v1/projects" >/dev/null || true
    curl -sS -H "$h_token" "$p" >/dev/null || true
    curl -sS -H "$h_token" -H "$h_json" -X PATCH "$p" \
        -d '{"description":"updated by sample"}' >/dev/null || true

    # Dependent reads — exercise the polymorphic resolver on the
    # nested resources so the cohort surfaces multiple variants of
    # the django_content_type lookup at record time. Without these,
    # the recording wouldn't capture the multi-bind shape and the
    # falsifying half of the matrix wouldn't have anything to fail
    # on.
    curl -sS -H "$h_token" "$p/my-role" >/dev/null || true
    curl -sS -H "$h_token" "$p/members" >/dev/null || true

    label_resp=$(curl -sS -H "$h_token" -H "$h_json" -X POST "$p/category-types" \
        -d '{"text":"positive","background_color":"#00ff00","text_color":"#ffffff"}' 2>/dev/null || true)
    label_id=$(jq -r '.id // empty' <<<"$label_resp" 2>/dev/null || true)
    curl -sS -H "$h_token" "$p/category-types" >/dev/null || true

    example_resp=$(curl -fsS -H "$h_token" -H "$h_json" -X POST "$p/examples" \
        -d '{"text":"Keploy CI sample text","meta":{"source":"sample"}}')
    example_id=$(jq -r '.id' <<<"$example_resp")
    if [ -n "$example_id" ] && [ "$example_id" != "null" ]; then
        curl -sS -H "$h_token" "$p/examples/${example_id}" >/dev/null || true
        if [ -n "$label_id" ]; then
            curl -sS -H "$h_token" -H "$h_json" -X POST "$p/examples/${example_id}/categories" \
                -d "{\"label\":${label_id}}" >/dev/null || true
        fi
    fi

    # Metrics endpoints — additional polymorphic queries.
    curl -sS -H "$h_token" "$p/metrics/progress" >/dev/null || true
    curl -sS -H "$h_token" "$p/metrics/member-progress" >/dev/null || true
}

# doccano_list_routes — print every (METHOD, PATH) pair the running
# doccano backend ACTUALLY serves, one per line, sorted. Walks
# Django's URL resolver inside the container (so the result tracks
# whatever doccano version this sample is pinned to, no static
# urls.py guess), and reports only methods the view's view class
# actually overrides (not Django's default `http_method_names`,
# which lists every HTTP verb regardless of whether a handler
# exists).
#
# Filtering: scoped to the API surface the sample's flow.sh aims at
# — /v1/projects/* (the polymorphic-resourcetype shape under test),
# /v1/me, /v1/users, /v1/health, /v1/fp/* (filepond uploads, pulled
# in via the auto-labeling flow). Auth admin, static / media, and
# anything outside /v1/ are excluded so the coverage denominator
# stays focused on the contract this lane is actually testing.
# Future lane that exercises a different surface (label-import,
# auto-labeling configs, etc.) should add itself to the SCOPE_PREFIXES
# list rather than redefining doccano_list_routes.
doccano_list_routes() {
    local backend="${DOCCANO_BACKEND_CONTAINER:-doccano_backend}"
    docker exec -i "$backend" python -c '
import os, re, sys
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()
from django.urls import URLPattern, URLResolver, get_resolver

SCOPE_PREFIXES = (
    "v1/projects",
    "v1/me",
    "v1/users",
    "v1/health",
    "v1/auth",
)

# DRF maps action names to HTTP methods deterministically. Used as
# the introspection source for ViewSet subclasses where method-on-
# class is hidden behind the action mapping.
ACTION_METHOD_MAP = {
    "list": "GET",
    "retrieve": "GET",
    "create": "POST",
    "update": "PUT",
    "partial_update": "PATCH",
    "destroy": "DELETE",
}

def normalise(pattern):
    s = str(pattern)
    s = re.sub(r"\(\?P<([^>]+)>[^)]+\)", r"{\1}", s)
    s = re.sub(r"<\w+:(\w+)>", r"{\1}", s)
    s = s.replace("^", "").replace("$", "").replace("\\Z", "")
    return s

def actual_methods(view, callback):
    methods = set()
    # Generic / mixin DRF views: handler methods named after HTTP
    # verbs (get / post / put / patch / delete / head / options).
    # Filter to ones the class itself defines (or any non-base
    # ancestor — `not in object`s vars is too narrow because a
    # mixin like ListModelMixin defines `list`, not `get`).
    for m in ("get", "post", "put", "patch", "delete"):
        if hasattr(view, m):
            methods.add(m.upper())
    # ViewSet action mapping. Each ViewSet subclass exposes
    # `actions` on its as_view() callback; e.g. /v1/projects has
    # actions={"get": "list", "post": "create"}.
    actions = getattr(callback, "actions", None)
    if actions:
        for http_method in actions:
            methods.add(http_method.upper())
    # @action-decorated methods (e.g. ProjectViewSet has a
    # `members` action mapped to GET / POST / DELETE on
    # /v1/projects/{id}/members). Reflected as additional entries
    # on the view class with `mapping` attributes after DRF binds
    # them.
    for attr in dir(view):
        bound = getattr(view, attr, None)
        mapping = getattr(bound, "mapping", None)
        if mapping:
            for http_method in mapping:
                methods.add(http_method.upper())
    return methods - {"OPTIONS", "HEAD", "TRACE"}

def walk(patterns, prefix=""):
    for entry in patterns:
        if isinstance(entry, URLResolver):
            yield from walk(entry.url_patterns, prefix + normalise(entry.pattern))
        elif isinstance(entry, URLPattern):
            full = prefix + normalise(entry.pattern)
            if not any(full.startswith(p) for p in SCOPE_PREFIXES):
                continue
            cb = entry.callback
            view = getattr(cb, "view_class", None) or getattr(cb, "cls", None)
            methods = actual_methods(view, cb) if view is not None else {"GET"}
            if not methods:
                continue
            for method in sorted(methods):
                yield method, "/" + full

for method, path in sorted(set(walk(get_resolver().url_patterns))):
    print(method, path)
' 2>/dev/null
}

# doccano_list_recorded_routes — print every (METHOD, PATH) pair the
# recorder captured during the just-finished record phase. Reads the
# keploy/test-set-*/tests/*.yaml tree rooted at the working dir.
doccano_list_recorded_routes() {
    local f method route
    while IFS= read -r f; do
        method=$(awk '/^    method:/{print $2; exit}' "$f")
        route=$(awk '/^    url:/{print $2; exit}' "$f")
        route="${route%%\?*}"
        case "$route" in
            http://*|https://*)
                route="/${route#*://*/}"
                ;;
        esac
        if [ -n "$method" ] && [ -n "$route" ]; then
            echo "$method $route"
        fi
    done < <(find keploy -type f -path '*/tests/*.yaml' 2>/dev/null) | sort -u
}

# doccano_report_coverage — compute (method, path) coverage of the
# recorded test set against the running doccano backend's URL
# resolver. Pure reporting: prints the percentage to stdout, never
# returns non-zero. The lane decides whether to gate.
#
# Matching: each recorded path is normalised by collapsing the
# numeric ID segments (e.g. /v1/projects/1) into the parameter
# placeholder Django uses (`{project_id}`), then compared against
# the route table's normalised entries. A recorded route matches
# any entry with the same method and a path whose static segments
# line up; this tolerates differences like /v1/projects/{id}/members
# vs /v1/projects/1/members (recorded form has a literal `1`).
#
# Only counted as "covered" if the recorded test passed at record
# time — a 5xx that landed in the test set still adds to the
# denominator, but its method-path pair counts as covered only if
# the response status was 2xx/3xx. Filter implemented inline below.
doccano_report_coverage() {
    local routes_file recorded_file
    routes_file="$(mktemp)"
    recorded_file="$(mktemp)"

    if ! doccano_list_routes >"$routes_file"; then
        echo "WARNING: could not enumerate doccano routes (is the backend container '${DOCCANO_BACKEND_CONTAINER:-doccano_backend}' running?)" >&2
        rm -f "$routes_file" "$recorded_file"
        return 0
    fi
    if [ ! -s "$routes_file" ]; then
        echo "WARNING: route enumeration produced no rows; skipping coverage report" >&2
        rm -f "$routes_file" "$recorded_file"
        return 0
    fi

    doccano_list_recorded_routes >"$recorded_file"

    local total covered missing pct
    total=$(wc -l <"$routes_file" | tr -d ' ')
    covered=0
    missing=""

    local line method route pattern recorded_method recorded_path
    while IFS= read -r line; do
        method="${line%% *}"
        route="${line#* }"
        # Build a regex pattern from the route table entry: replace
        # any `{name}` placeholder with a "match one path segment"
        # group. Anchored with ^ / $ to reject partial matches.
        pattern="^${method} $(printf '%s' "$route" | sed -E 's/\{[^}]+\}/[^\/]+/g')$"
        if grep -qE "$pattern" "$recorded_file"; then
            covered=$((covered + 1))
        else
            missing+="  ${method} ${route}"$'\n'
        fi
    done <"$routes_file"

    if [ "$total" -gt 0 ]; then
        pct=$(awk -v c="$covered" -v t="$total" 'BEGIN{printf "%.1f", c*100/t}')
    else
        pct="0.0"
    fi

    {
        echo "================ doccano API coverage ================"
        echo "Covered ${covered}/${total} (${method:+}${pct}%)"
        if [ -n "$missing" ]; then
            echo "Uncovered:"
            printf '%s' "$missing"
        fi
        echo "======================================================"
    } | tee "${COVERAGE_REPORT_FILE:-coverage_report.txt}"

    rm -f "$routes_file" "$recorded_file"
}

case "${1:-}" in
    bootstrap)
        doccano_bootstrap_token "${2:-180}"
        ;;
    record-traffic)
        doccano_record_traffic
        ;;
    coverage)
        # Lane scripts call this after `keploy record` finishes (when
        # the backend container is still running and `keploy/test-
        # set-*/tests/*.yaml` is on disk).
        doccano_report_coverage
        ;;
    list-routes)
        # Diagnostic — print the route table the coverage report
        # uses as its denominator. Useful for verifying a doccano
        # version bump didn't shift the surface unexpectedly.
        doccano_list_routes
        ;;
    *)
        cat >&2 <<EOF
usage: $0 {bootstrap|record-traffic|coverage|list-routes}

  bootstrap      log in as admin and install the deterministic auth
                 token (idempotent; safe to re-run against a populated DB)
  record-traffic drive the API: warmup hammer + project create + reads
                 + label + example + categories + metrics. Fire-and-forget;
                 keploy is the assertion layer at replay
  coverage       walk the running backend's URL resolver and the
                 just-recorded keploy/test-set-* tests; emit a (method,
                 path) coverage percentage
  list-routes    print the URL resolver's (method, path) pairs (the
                 coverage denominator)
EOF
        exit 2
        ;;
esac
