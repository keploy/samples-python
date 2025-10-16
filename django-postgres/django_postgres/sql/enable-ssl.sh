#!/usr/bin/env bash
set -e

# Generate a self-signed server cert the first time the cluster initializes
if [[ ! -f "$PGDATA/server.crt" ]]; then
  openssl req -new -x509 -days 365 -nodes -text \
    -subj "/CN=postgres_ssl" \
    -keyout "$PGDATA/server.key" \
    -out "$PGDATA/server.crt"
  chmod 600 "$PGDATA/server.key" "$PGDATA/server.crt"
  chown postgres:postgres "$PGDATA/server.key" "$PGDATA/server.crt"
  echo "ssl = on" >> "$PGDATA/postgresql.conf"
  echo "ssl_cert_file = 'server.crt'" >> "$PGDATA/postgresql.conf"
  echo "ssl_key_file  = 'server.key'"  >> "$PGDATA/postgresql.conf"
fi
