#!/bin/sh
# wait-for-postgres.sh

echo "start-wait-for-postgres.sh"

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER"
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd