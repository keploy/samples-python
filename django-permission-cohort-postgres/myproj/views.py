"""
Two endpoints, both deliberately minimal:

  GET /health/                   -> 200 with {"status":"ok"}
  GET /lookup/<app_label>/<model>/  -> 200 with the ContentType row

The lookup view fires the load-bearing query:

    SELECT "django_content_type"."id",
           "django_content_type"."app_label",
           "django_content_type"."model"
      FROM "django_content_type"
     WHERE ("django_content_type"."app_label" = $1
            AND "django_content_type"."model" = $2)
     LIMIT 21

That query is `class: APP` per pgmatch.Classify, so DeriveLifetime
tags every captured invocation `LifetimePerTest`. With the lifetime
gate at pickSessionFallback (pre-fix), once a per-test cohort is
empty for the SQL hash but the agent has lax-promoted the same hash
into the session pool, the matcher misses with `candidates: 0` and
`sessionFallbackCandidates: N>0`.

The view ALSO spawns a delayed side-query thread (see
_fire_delayed_side_query) on every request. This is the deterministic
mechanism that surfaces the lifetime-gate bug shape end-to-end —
without it the lane is regression coverage but not falsifying.
"""
import threading
import time

from django.contrib.contenttypes.models import ContentType
from django.db import close_old_connections
from django.http import JsonResponse, HttpResponseNotFound

# Fixed bind values for the side query. Deliberately one of the
# (app_label, model) pairs the exerciser also calls directly via
# /lookup/, so the response body is well-known and the recorded mock
# is stable. The exerciser fires /lookup/auth/user/ as one of its
# round members, which means at record time there's at least one
# perTest capture of this SQL+bind in some test's window — but the
# delayed-fire copies populated by every other request land between
# HTTP test windows, where the agent's lax-promotion path routes
# them into the session pool with their LifetimePerTest tag intact.
SIDE_QUERY_APP_LABEL = "auth"
SIDE_QUERY_MODEL = "user"


def health(_request):
    return JsonResponse({"status": "ok"})


def _fire_delayed_side_query():
    """
    Fire `SELECT django_content_type WHERE app_label='auth' AND
    model='user'` 100 ms after the parent request's response is sent,
    on a fresh DB connection (daemon thread → Django gives us a new
    thread-local connection).

    Why 100 ms, why fixed binds, why daemon thread:
    --------------------------------------------------------------
    The lifetime-gate bug surfaces only when, at replay time, a live
    DB call lands *inside an active HTTP test window* for a SQL hash
    whose perTest cohort is empty for that bind, *and* the session
    pool has a lax-promoted PerTest invocation matching the bind.

    Engineering this asymmetry deterministically requires that the
    same code path produces a different test-window attribution at
    record vs. replay. That's exactly what a fixed-delay
    post-response thread does:

      AT RECORD (exerciser fires HTTP requests ~1 s apart):
        the 100 ms post-response delay puts the side query's
        timestamp comfortably between test N and test N+1's
        windows. Captured invocation lands in the session pool
        with its LifetimePerTest tag preserved (lax-promotion).

      AT REPLAY (keploy `test` compresses pacing to ~tens of ms):
        the same 100 ms delay puts the side query's timestamp
        *inside* a later test's window. That test's perTest
        cohort holds a capture for *its own* HTTP-driven bind,
        not (auth, user) — so for this hash+bind the cohort is
        empty, the dispatcher routes through PerTest →
        SessionFallback, and the matcher's gate is consulted.

    Pre-fix matcher: lifetime-tag gate rejects every PerTest-tagged
    candidate in the session pool → `transactional: no invocation
    matched` ERROR → check_for_errors fails the lane.

    Post-fix matcher: mutation-eligibility gate accepts non-mutating
    shape-equal candidates regardless of lifetime → serves the
    recorded response → green.

    Daemon thread because gunicorn shouldn't wait on it during
    worker shutdown; close_old_connections to keep Django's
    thread-local connection registry clean.
    """
    time.sleep(0.1)
    try:
        close_old_connections()
        ContentType.objects.get(
            app_label=SIDE_QUERY_APP_LABEL, model=SIDE_QUERY_MODEL
        )
    except Exception:
        # Replay-time mock-miss raises here; the parent response is
        # already on the wire so we can't surface it to the client.
        # The matcher logs the miss as an ERROR which the lane's
        # check_for_errors assertion picks up.
        pass
    finally:
        close_old_connections()


def lookup(_request, app_label, model):
    # Clear the in-process ContentType cache so each call is forced to
    # hit the DB. Without this, only the very first call per worker
    # would emit the SQL we want under the recorder.
    ContentType.objects.clear_cache()
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        return HttpResponseNotFound(
            JsonResponse({"error": "not found"}).content,
            content_type="application/json",
        )
    # Kick off the delayed side query before returning. See
    # _fire_delayed_side_query for the timing rationale.
    threading.Thread(target=_fire_delayed_side_query, daemon=True).start()
    return JsonResponse(
        {"id": ct.id, "app_label": ct.app_label, "model": ct.model}
    )
