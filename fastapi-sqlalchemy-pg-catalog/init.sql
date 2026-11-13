-- Pre-create the `project` table so SQLAlchemy's create_all() sees it
-- exists at record time and skips CREATE TABLE. This is what the bug
-- (keploy/integrations#193) requires: at record time the pg_class
-- probe answers "table exists", so CREATE TABLE is never sent and
-- never recorded. At replay time, if the simple-query dispatcher path
-- skips the recorded mock, the synthetic catalog engine returns zero
-- rows, SQLAlchemy concludes "table missing", and issues an
-- unrecorded CREATE TABLE -- which then misses the transactional
-- engine, raises a DatabaseError, and kills app boot.
CREATE TABLE IF NOT EXISTS project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Seed the table. The Postgres entrypoint runs scripts under
-- /docker-entrypoint-initdb.d only on first init (empty data dir),
-- so this is single-shot on a clean container. If you reuse a stale
-- data volume, this script doesn't run at all — re-create the
-- volume (`docker compose down -v`) for a deterministic repro.
INSERT INTO project (name) VALUES ('seed');
