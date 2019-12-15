FROM python:3.7-alpine

ARG POETRY_VERSION=1.0.0

WORKDIR /work

COPY . /usr/src/preacher
RUN apk --no-cache add libxml2 libxslt && \
    apk --no-cache add --virtual .build-deps \
        libc-dev \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        openssl-dev \
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
    poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    \
    python get-poetry.py --uninstall --yes && \
    \
    pip --no-cache-dir install . && \
    rm -rf $HOME/.cache && \
    \
    cd $HOME && \
    rm -rf /usr/src/preacher && \
    \
    apk --no-cache del .build-deps && \
    \
    preacher-cli --version
