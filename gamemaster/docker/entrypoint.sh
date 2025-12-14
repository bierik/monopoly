#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
rm -f /tmp/startup-complete

: "${DJANGO_DATABASE_HOST:=db}"

echo "⏳ POSTGRES: await host '$DJANGO_DATABASE_HOST'."
timeout -f 10 bash -c "until pg_isready -qh \"$DJANGO_DATABASE_HOST\"; do sleep 0.5; done" && echo "🥳 POSTGRES: ready." || (echo -e "\n❌ POSTGRES: timeout." >&2; exit 1)

if [ "${DJANGO_CONFIGURATION:-}" = "DockerTesting" ]; then
    echo "⏳ PLAYWRIGHT: await."
    timeout -f 10 bash -c "until nc -z playwright 8000 >/dev/null 2>&1; do sleep 0.5; done" && echo "🥳 PLAYWRIGHT: ready." || (echo -e "\n❌ PLAYWRIGHT: timeout." >&2; exit 1)
else
    python manage.py migrate --noinput
fi

touch /tmp/startup-complete
exec "$@"
