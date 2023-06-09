FROM python:3.10-slim-bullseye AS base

# Setup environment variables.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

# Setup directory, group, and user - then install common dependencies.
RUN mkdir -p /hitas/backend \
    && addgroup \
      --gid 1000 hitas \
    && adduser \
      --disabled-login \
      --ingroup hitas \
      --no-create-home \
      --home /nonexistent \
      --gecos "hitas user" \
      --shell /bin/false \
      --uid 1000 hitas \
    && chown hitas:hitas /hitas \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      libpq5 \
      gettext \
      mime-support \
      libpcre3 \
      libpcre3-dev \
      postgresql

FROM base AS builder

# Setup environment variables for poetry.
ENV POETRY_VERSION=1.3.1
ENV POETRY_HOME=/usr/pypoetry
ENV PATH=$POETRY_HOME/bin:$PATH
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Install build dependencies
RUN apt-get install -y --no-install-recommends \
      curl \
      libpq-dev \
      build-essential

# Install poetry.
RUN curl -sSL https://install.python-poetry.org | python -

# Copy poetry files.
COPY poetry.lock pyproject.toml /

# Create virtualenv.
RUN python -m venv /hitas/venv

# Activate virtualenv by setting some environment variables.
ENV PATH=/hitas/venv/bin:$PATH
ENV VIRTUAL_ENV=/hitas/venv

# Install production dependencies (to previously created virtualenv).
RUN poetry install --no-root --only main

FROM base AS django-build-static

# Copy virtualenv.
COPY --chown=hitas:hitas --from=builder /hitas/venv /hitas/venv

# Activate virtualenv by setting some environment variables.
ENV PATH=/hitas/venv/bin:$PATH
ENV VIRTUAL_ENV=/hitas/venv
ENV SECRET_KEY=xxx

# Change working directory to project directory.
WORKDIR /hitas/backend/

# Copy project files.
COPY . .

# Collect static files and compile translations
RUN python manage.py collectstatic --clear --no-input --verbosity=2  \
    && python manage.py compilemessages -l "fi"

FROM base AS production

# Switch to restricted user and working directory.
USER hitas
WORKDIR /hitas/backend/

# Copy project files, virtualenv, static files, and translations.
COPY --chown=hitas:hitas . .
COPY --chown=hitas:hitas --from=builder /hitas/venv /hitas/venv
COPY --chown=hitas:hitas --from=django-build-static /hitas/backend/static /hitas/backend/static

ENTRYPOINT ["/hitas/backend/docker-entrypoint.sh"]
