#!/usr/bin/env sh
set -e

# If a database URL is used, you might wait for it here. For sqlite this is a no-op.
echo "Running entrypoint: applying migrations and collecting static files"

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

exec "$(cat /proc/1/cmdline | tr '\0' ' ' )" || exec "$@"
