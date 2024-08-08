#!/bin/sh

until nc -z -v -w30 postgres 5432
do
  echo "Waiting for database connection..."
  # wait for 5 seconds before check again
  sleep 5
done

uvicorn application.main:app --host 0.0.0.0 --port 8000
