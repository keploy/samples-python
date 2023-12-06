SELECT 'CREATE DATABASE usersdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'usersdb')\gexec