#!/bin/bash

set -euo pipefail

echo "Version: $VERSION"

# Apply or validate database migrations
if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
else
    echo "Checking that migrations are applied..."
    error_code=0
    ./manage.py migrate --check || error_code=$?

    if [ "$error_code" -ne 0 ]; then
        echo "Migrations are not applied!"
        exit $error_code
    fi
fi

# Collect static files
echo "Collecting static files..."
./manage.py collectstatic --noinput

# Translate messages
echo "Updating translations..."
./manage.py compilemessages -l "fi"

# Start server
if [[ -n "$*" ]]; then
    echo "Running command" "$@"
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    echo "Starting dev-server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting uwsgi-server..."
    exec uwsgi --ini uwsgi_docker.ini
fi
