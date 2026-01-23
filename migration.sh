#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

for i in {1..60}; do
  if (echo > /dev/tcp/postgres/5432) >/dev/null 2>&1; then
    echo "PostgreSQL is up - executing migrations"
    break
  fi
  echo "Waiting... ($i/60)"
  sleep 5
done

if [ $i -gt 60 ]; then
  echo "Error: PostgreSQL did not become available"
  exit 1
fi

cd /app/api
alembic -c migrations/alembic.ini upgrade head || echo "Migration already up to date or skipped"

exec /entrypoint.sh "$@"