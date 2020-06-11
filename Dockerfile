FROM alpine:3.12

WORKDIR /work

COPY . /usr/src/preacher
RUN apk --no-cache add python3 libxml2 libxslt && \
    apk --no-cache add --virtual .build-deps \
        python3-dev \
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
        && \
    \
    python3 -m ensurepip && \
    pip3 --no-cache-dir install /usr/src/preacher && \
    rm -rf /usr/src/preacher $HOME/.cache && \
    \
    apk --no-cache del .build-deps && \
    \
    preacher-cli --version
