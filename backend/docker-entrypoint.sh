#!/usr/bin/env bash

set -euo pipefail

VERSION=${VERSION:-"<unknown>"}

echo
echo "Version: ${VERSION}"
echo

. /hitas/venv/bin/activate

if [[ "${RESET_MIGRATIONS:-"0"}" = "1" ]]; then
    echo "Resetting migrations..."
    ./manage.py migrate hitas zero
    echo
fi

# Apply or validate database migrations
if [[ "${APPLY_MIGRATIONS:-"0"}" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
    echo
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
    error_code=0
    ./manage.py hitasmigrate --check || error_code=$?

    if [ "${error_code}" -ne 0 ]; then
        echo "Initial dataset is not applied! Migration already done!"
    else
        echo "Loading initial dataset..."
        ./manage.py loaddata initial.json
    fi
fi

# Start server
echo
echo "Starting uwsgi-server..."
echo
exec uwsgi --ini uwsgi.ini
