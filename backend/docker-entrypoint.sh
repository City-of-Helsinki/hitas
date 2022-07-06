#!/usr/bin/env bash

set -euo pipefail

VERSION=${VERSION:-""}

echo "Version: ${VERSION}"

. /hitas/venv/bin/activate

# Apply or validate database migrations
if [[ "${APPLY_MIGRATIONS:-"0"}" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
else
    echo "Checking that migrations are applied..."
    error_code=0
    ./manage.py migrate --check || error_code=$?

    if [ "${error_code}" -ne 0 ]; then
        echo "Migrations are not applied!"
        exit ${error_code}
    fi
fi

# Apply initial dataset
if [[ "${LOAD_INITIAL_DATASET:-"0"}" = "1" ]]; then
    ./manage.py loaddata initial.json
fi

# Start server
echo
echo "Starting uwsgi-server..."
echo
exec uwsgi --ini uwsgi.ini
