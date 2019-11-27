FROM python:3.8-alpine

ARG POETRY_VERSION=0.12.17

WORKDIR /work

COPY . /usr/src/preacher
RUN apk --no-cache add libxml2 libxslt && \
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
    cd /usr/src/preacher && \
    \
    curl -sSLO https://raw.githubusercontent.com/sdispater/poetry/$POETRY_VERSION/get-poetry.py && \
    python get-poetry.py && \
    source $HOME/.poetry/env && \
    \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev && \
    pip --no-cache-dir install . && \
    \
    python get-poetry.py --uninstall --yes && \
    rm -rf $HOME/.cache && \
    \
    cd $HOME && \
    rm -rf /usr/src/preacher && \
    \
    apk --no-cache del .build-deps && \
    \
    preacher-cli --version
