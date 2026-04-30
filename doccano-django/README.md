# doccano-django — keploy postgres-v3 simple-Query bind regression sample

Minimal reproducer for the doccano polymorphic-resourcetype failure
that motivated [keploy/integrations#177](https://github.com/keploy/integrations/pull/177)
("fix(postgres-v3): extract simple-Query literals into bindValues").

The sample wraps doccano (Django + django-rest-polymorphic + psycopg2)
at version `v1.8.5` against postgres `13.3-alpine`. The shape under
test: a polymorphic Django model (`Project` with subclass
`TextClassificationProject`) created over the REST API and re-read via
DRF's polymorphic queryset. Without the integrations fix, every
`SELECT … FROM django_content_type WHERE app_label = $1 AND model = $2`
at replay returns the same recorded mock (the matcher's
`pickSessionFallback` FIFO-collapses every variant onto the first
recording when the bind signature is empty), so the polymorphic
serializer can't resolve the project's subclass and `resourcetype`
flips from `"TextClassificationProject"` to `"Project"`.

The bug is in keploy's recorder + replayer simple-Query path; doccano
is just a vehicle. Same pattern would reproduce on any Django app
that:

* Uses a polymorphic ORM (django-polymorphic / django-rest-polymorphic).
* Sends parameterised reads via psycopg2's simple-Query mode
  (literals interpolated into the SQL text rather than carried in a
  separate Bind packet).
* Exercises the polymorphic queryset across multiple HTTP requests
  against the same recorded backend.

## What's in here

* `Dockerfile` — thin wrapper around `doccano/doccano:backend` pinning
  the upstream version this sample tracks. Future doccano releases
  that change the bug-triggering shape are addressed by retagging
  here, not by scattering version pins across the lane scripts in
  `keploy/integrations` / `keploy/enterprise`.
* `docker-compose.yml` — the orchestration: postgres-13 alongside
  the doccano backend, on a fixed subnet so the lane scripts can
  rely on stable IPs across record/replay phases.
* `flow.sh` — the minimum reproducer traffic, ~10 HTTP calls. POST
  `/v1/projects` (creates a `TextClassificationProject`), then GET
  list / GET single / PATCH single / a few dependent reads. The
  GET / PATCH responses are what diverge under the bug — POST
  passes either way because the in-memory subclass instance shapes
  the response without consulting the DB.
* `keploy.yml.template` — keploy config skeleton (proxy port, DNS
  port, container name placeholders) that lane scripts in
  `keploy/integrations` and `keploy/enterprise` `envsubst` into a
  per-job copy.

## Running locally

```sh
# Bring doccano up + bootstrap the admin token (one-shot; the volume
# is reused for the actual record run).
docker compose up -d
./flow.sh bootstrap

# Record
keploy record \
  -c "docker compose up" \
  --container-name doccano_backend \
  --proxy-port 18081 --dns-port 18082

# (in another shell, while keploy record is up)
./flow.sh record-traffic
# → SIGINT keploy when traffic returns

# Replay
keploy test \
  -c "docker compose up" \
  --containerName doccano_backend \
  --apiTimeout 60 --delay 20 \
  --proxy-port 18081 --dns-port 18082
```

Expected outcome with the integrations fix in place: 0 failures,
all `is_text_project: true` / `resourcetype: "TextClassificationProject"`
across the project-read responses.

Expected outcome **without** the fix: tests covering GET-after-POST
project reads fail with `is_text_project: true → false` and
`resourcetype: "TextClassificationProject" → "Project"`.

## CI lanes that consume this sample

* `keploy/integrations` — `.woodpecker/doccano-postgres.yml` /
  `.ci/scripts/python/doccano/doccano-linux.sh`. Three-way matrix
  (record-build × replay-build, record-latest × replay-build,
  record-build × replay-latest) — the cross-binary cells stay red
  until both keploy releases pick up the bind-extraction fix.
* `keploy/enterprise` — `.woodpecker/doccano-linux.yml` /
  `.ci/scripts/doccano-linux.sh`. Same three-way matrix wired to
  the enterprise compat-matrix harness.

Both clone this directory at the branch / tag pinned by the
respective lane script.

## Related

* [keploy/integrations#177](https://github.com/keploy/integrations/pull/177) — the fix this sample falsifies.
* [keploy/enterprise#1889](https://github.com/keploy/enterprise/pull/1889) — original failing PR where the bug surfaced.
* [django-rest-polymorphic](https://github.com/apirobot/django-rest-polymorphic) — the upstream library whose serialisation path the bug breaks.
