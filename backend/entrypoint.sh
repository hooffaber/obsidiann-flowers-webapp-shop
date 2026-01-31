#!/bin/sh
set -e

# Ensure media directory exists
mkdir -p /app/src/media

# Run migrations only for the main app (gunicorn), not for celery workers
if [ "$1" = "gunicorn" ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

echo "Starting: $@"
exec "$@"
