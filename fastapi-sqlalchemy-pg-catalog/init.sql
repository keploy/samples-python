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

-- Seed the table.
--
-- Postgres only runs scripts under /docker-entrypoint-initdb.d on
-- *first* database initialization (empty data dir), so on a clean
-- container this is a single-shot insert and `ON CONFLICT` /
-- `NOT EXISTS` wouldn't normally matter. The `NOT EXISTS` guard is
-- defensive belt-and-suspenders for the degenerate case where the
-- compose stack reuses a stale Postgres data volume that already
-- carries the seed row — it keeps the script idempotent without
-- requiring a UNIQUE constraint on project.name (which the
-- SQLAlchemy model doesn't declare).
INSERT INTO project (name)
SELECT 'seed'
WHERE NOT EXISTS (SELECT 1 FROM project WHERE name = 'seed');
