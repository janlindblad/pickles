#!/usr/bin/env sh
set -e

# If a database URL is used, you might wait for it here. For sqlite this is a no-op.
echo "Running entrypoint: applying migrations and collecting static files"

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Set default port if not provided
PORT=${PORT:-8080}

# If the command is gunicorn, make sure it uses the PORT environment variable
if [ "$1" = "gunicorn" ]; then
    exec gunicorn pickles.wsgi:application -b "0.0.0.0:$PORT" --workers 3
else
    # Execute the command passed to the container
    exec "$@"
fi
