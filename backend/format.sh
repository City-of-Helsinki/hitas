#!/bin/sh

cmd='autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports . && isort . && black . && flake8 .'

if [ -f /.dockerenv ]; then
    eval "$cmd"
else
    docker-compose run --no-deps --rm --entrypoint='/bin/sh -c' hitas "$cmd"
fi
