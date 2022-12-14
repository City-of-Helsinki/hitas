FROM python:3.10-slim-bullseye as base

#
# Set python defaults
#
ENV PYTHONUNBUFFERED 1 \
    PYTHONFAULTHANDLER 1 \
    PYTHONHASHSEED=random

#
# Create user and directory for hitas
#
RUN mkdir /hitas && \
    addgroup --gid 1000 hitas && \
    adduser --disabled-login --ingroup hitas --no-create-home --home /nonexistent --gecos "hitas user" --shell /bin/false --uid 1000 hitas && \
    chown hitas:hitas /hitas

#
# Install common depedencies
#
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        gettext \
        mime-support \
        libpcre3 libpcre3-dev

#
# Build virtualenv
#
FROM base AS builder

#
# Install depedencies for building
#
RUN apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential

#
# Set defaults for pip and poetry
#
ENV POETRY_VERSION=1.3.1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

#
# Poetry installation
#
RUN pip install "poetry==$POETRY_VERSION"


#
# Create virtualenv and install dependencies
#
USER hitas
RUN python -m venv /hitas/venv && /hitas/venv/bin/pip install wheel

RUN mkdir /hitas/build
WORKDIR /hitas/build
COPY --chown=hitas:hitas poetry.lock pyproject.toml ./
RUN poetry export --without-hashes | /hitas/venv/bin/pip install -r /dev/stdin

#
# Build image for django static content and translations
#
FROM base AS django-build-static

# Copy virtualenv
COPY --from=builder --chown=hitas:hitas /hitas/venv /hitas/venv

RUN mkdir -p /hitas/backend
WORKDIR /hitas/backend

COPY manage.py ./
COPY hitas ./hitas
COPY config ./config
COPY users ./users

RUN . /hitas/venv/bin/activate && SECRET_KEY=xxx ./manage.py collectstatic --clear --no-input --verbosity=0
RUN . /hitas/venv/bin/activate && SECRET_KEY=xxx ./manage.py compilemessages -l "fi"

#
# Build nginx image
#
FROM nginx:1.23-alpine AS nginx

ADD nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=django-build-static --chown=nginx:nginx /hitas/backend/var/static /media/static

#
# Build the backend image
#
FROM base

# Copy virtualenv
COPY --from=builder --chown=hitas:hitas /hitas/venv /hitas/venv

USER hitas
RUN mkdir -p /hitas/backend
WORKDIR /hitas/backend
COPY --chown=hitas:hitas docker-entrypoint.sh ./
ENTRYPOINT ["/hitas/backend/docker-entrypoint.sh"]

COPY --chown=hitas:hitas manage.py uwsgi.ini ./
COPY --chown=hitas:hitas hitas ./hitas
COPY --chown=hitas:hitas config ./config
COPY --from=django-build-static --chown=hitas:hitas /hitas/backend/config/locale ./config/
COPY --chown=hitas:hitas templates ./templates
COPY --chown=hitas:hitas users ./users
COPY --chown=hitas:hitas initial.json ./

EXPOSE 8888 8080
