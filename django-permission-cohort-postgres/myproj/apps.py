"""
AppConfig that spawns a background ContentType-lookup thread inside
each gunicorn worker.

Why this exists
---------------
The keploy/integrations django-permission-cohort-postgres lane is a
falsifying e2e lane for the postgres-v3 session-fallback lifetime-gate
fix (keploy/enterprise#1952). To produce the bug shape end-to-end,
the recording must capture some `SELECT django_content_type`
invocations whose request-timestamp falls *between* the surrounding
HTTP test windows. Those out-of-window captures are routed by the
keploy agent's lax-promotion path
(FilterPerTestAndLaxPromotedTierAware in keploy/keploy:pkg/util.go)
into the session pool — preserving their on-disk
`lifetime: perTest` tag. Replay-side, the live request that fires
during a test whose perTest cohort is empty for that SQL hash falls
through to the session-fallback path; pre-fix the lifetime gate
silently rejected the lax-promoted invocation, post-fix the
mutation-aware gate accepts it.

The lane's HTTP-driven exerciser alone can't produce that shape: any
query fired inside an HTTP request lands inside that test's window
and ends up in its perTest cohort, never out-of-window. We need
DB activity that fires *outside* the HTTP request path.

This thread provides that: each gunicorn worker spawns one daemon
thread that periodically clears Django's in-process ContentType
cache, runs a fresh `ContentType.objects.get(...)` (which forces the
SQL the bug surfaces on), and sleeps. The cadence (default 3s) is
slow enough not to swamp the worker pool but fast enough that the
exerciser's 6s inter-round pause captures multiple thread-fired
queries between HTTP test windows.

The thread is gated behind the BACKGROUND_LOOKUPS env var so the
sample stays usable as a plain Django app for ad-hoc local testing.
The CI lane sets BACKGROUND_LOOKUPS=1.
"""
import logging
import os
import threading
import time

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class MyProjConfig(AppConfig):
    name = "myproj"
    default = True

    def ready(self):
        # `ready()` runs at most once per worker (Django guarantees idempotency
        # within a process), so the thread spawn is safe here. Daemon=True
        # ensures the thread doesn't block worker shutdown.
        if os.environ.get("BACKGROUND_LOOKUPS", "0") != "1":
            return
        # Lookup-target cycle — different (app_label, model) pairs to widen
        # the hash spectrum so the recording's session-fallback cohort isn't
        # a single-shape singleton. All target the same SQL hash (different
        # binds), which is the shape the lifetime-gate fix unblocks.
        targets = [
            ("auth", "user"),
            ("auth", "group"),
            ("auth", "permission"),
            ("contenttypes", "contenttype"),
        ]
        interval_s = float(os.environ.get("BACKGROUND_LOOKUPS_INTERVAL_S", "3"))

        def loop():
            # Lazy import — apps aren't all loaded at module-import time.
            from django.contrib.contenttypes.models import ContentType

            i = 0
            while True:
                try:
                    time.sleep(interval_s)
                    app_label, model = targets[i % len(targets)]
                    ContentType.objects.clear_cache()
                    ContentType.objects.get(app_label=app_label, model=model)
                    i += 1
                except Exception as exc:  # noqa: BLE001 — keep the thread alive
                    logger.warning("background lookup failed: %s", exc)

        threading.Thread(target=loop, daemon=True, name="bg-content-type-lookups").start()
        logger.info(
            "background ContentType-lookup thread started (interval=%ss, targets=%s)",
            interval_s,
            len(targets),
        )
