ARG VERSION=""

# ==============================
FROM python:3.10-slim-bullseye AS base
# ==============================
ENV PYTHONUNBUFFERED 1

RUN mkdir /hitas-backend && \
    groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -ms /bin/bash appuser

WORKDIR /hitas-backend

COPY poetry.lock pyproject.toml /hitas-backend/

RUN apt-get update && \
    mkdir -p /usr/share/man/man1/ /usr/share/man/man3/ /usr/share/man/man7/ && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        postgresql-client \
        gettext \
        mime-support \
        curl && \
    curl -sSL --retry 5 https://install.python-poetry.org | python - && \
    /root/.local/bin/poetry config virtualenvs.create false && \
    /root/.local/bin/poetry install --no-dev --no-interaction && \
    apt-get remove -y build-essential libpq-dev && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/archives && \
    rm -rf /root/.cache/pypoetry && \
    rm -rf /root/.cache/pip

COPY docker-entrypoint.sh /usr/local/bin
ENTRYPOINT ["docker-entrypoint.sh"]

# ==============================
FROM base AS development
# ==============================

ENV DEBUG=1
ENV APPLY_MIGRATIONS=1
ENV COLLECT_STATIC=1
ENV DEV_SERVER=1

RUN /root/.local/bin/poetry install
COPY . /hitas-backend
RUN chown -R appuser:appuser /hitas-backend
USER appuser
EXPOSE 8000

# ==============================
FROM base AS production
# ==============================
ARG VERSION

ENV VERSION=${VERSION}
ENV APPLY_MIGRATIONS=0
ENV COLLECT_STATIC=1

COPY . /hitas-backend

# OpenShift runs container in arbitrary user which belongs to group `root` (0)
RUN chgrp -R 0 /hitas-backend && \
    chmod -R g=u /hitas-backend
USER appuser:0

EXPOSE 8000
