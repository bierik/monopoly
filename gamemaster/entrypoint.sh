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
python manage.py devsetup --participations ${PARTICIPATIONS:-4}

exec "$@"
