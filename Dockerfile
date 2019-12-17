FROM python:3.8-alpine

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
    pip --no-cache-dir install /usr/src/preacher && \
    rm -rf /usr/src/preacher $HOME/.cache && \
    \
    apk --no-cache del .build-deps && \
    \
    preacher-cli --version
