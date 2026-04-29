"""
Two endpoints, both deliberately minimal:

  GET /health/                   -> 200 with {"status":"ok"}
  GET /lookup/<app_label>/<model>/  -> 200 with the ContentType row

The lookup view is the load-bearing one. It calls
ContentType.objects.clear_cache() before each lookup so the in-process
cache never short-circuits the query. Every request therefore fires:

    SELECT "django_content_type"."id",
           "django_content_type"."app_label",
           "django_content_type"."model"
      FROM "django_content_type"
     WHERE ("django_content_type"."app_label" = $1
            AND "django_content_type"."model" = $2)
     LIMIT 21

That query is `class: APP` per pgmatch.Classify (a SELECT from a
user-schema table, not pg_catalog), so DeriveLifetime tags every
captured invocation `LifetimePerTest`. With the lifetime gate at
pickSessionFallback (pre-fix), once a per-test cohort is empty for the
SQL hash but the agent has lax-promoted the same hash into the
session pool, the matcher misses with `candidates: 0` and
`sessionFallbackCandidates: N>0`. That's the doccano-shape failure
this lane regresses against.
"""
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseNotFound


def health(_request):
    return JsonResponse({"status": "ok"})


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
    return JsonResponse(
        {"id": ct.id, "app_label": ct.app_label, "model": ct.model}
    )
