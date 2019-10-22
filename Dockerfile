FROM python:3.7-alpine

ARG POETRY_VERSION=0.12.17

WORKDIR /work

COPY README.md pyproject.toml poetry.lock /usr/src/preacher/
COPY preacher /usr/src/preacher/preacher
RUN set -o pipefail && \
    \
    apk --no-cache add libxml2 libxslt && \
    apk --no-cache add --virtual .build-deps \
        libc-dev \
        libxml2-dev \
        libxslt-dev \
        libtool \
        autoconf \
        automake \
        make \
        gcc \
        curl \
        && \
    \
    curl -sSL \
        https://raw.githubusercontent.com/sdispater/poetry/$POETRY_VERSION/get-poetry.py \
        | python && \
    source ~/.poetry/env && \
    poetry config settings.virtualenvs.create false && \
    \
    cd /usr/src/preacher && \
    poetry install --no-dev && \
    cd ~ && \
    \
    poetry self:uninstall --yes && \
    rm -rf /usr/src/preacher ~/.cache && \
    apk --no-cache del .build-deps
