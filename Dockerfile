FROM alpine:3.16.0

WORKDIR /work

COPY . preacher
RUN apk --no-cache add python3 py3-lxml py3-yaml && \
    apk --no-cache add --virtual .build-deps \
        python3-dev \
        libc-dev \
        libffi-dev \
        openssl-dev \
        libtool \
        autoconf \
        automake \
        make \
        gcc \
        cargo \
        && \
    \
    python3 -m ensurepip && \
    \
    export CFLAGS='-O2 -g0 -pipe -fPIC -flto' && \
    export LDFLAGS='-flto' && \
    pip3 --no-cache-dir install ./preacher && \
    \
    rm -rf ./preacher ~/.cache ~/.cargo && \
    apk --no-cache del .build-deps && \
    \
    preacher-cli --version
