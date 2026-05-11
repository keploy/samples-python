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

-- Idempotent seed. `ON CONFLICT DO NOTHING` would only help with a
-- UNIQUE/EXCLUSION constraint on name, which the SQLAlchemy model
-- doesn't declare; use NOT EXISTS so re-running this script against
-- an existing volume doesn't duplicate the row.
INSERT INTO project (name)
SELECT 'seed'
WHERE NOT EXISTS (SELECT 1 FROM project WHERE name = 'seed');
