#!/bin/sh
set -o errexit
set -o pipefail
set -o nounset


export PGPASSWORD=$DJANGO_DATABASE_PASSWORD
until psql -h $DJANGO_DATABASE_HOST -U $DJANGO_DATABASE_USER -w -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

python manage.py migrate --noinput
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --username=admin --email=admin@example.org --no-input 1> /dev/null 2> /dev/null || true

exec "$@"
