FROM alpine:3.12.3

WORKDIR /work

COPY . preacher
RUN apk --no-cache add python3 yaml libxml2 libxslt && \
    apk --no-cache add --virtual .build-deps \
        python3-dev \
        yaml-dev \
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
    \
    export CFLAGS='-O2 -g0 -pipe -fPIC -flto' && \
    export LDFLAGS='-flto' && \
    pip3 --no-cache-dir install ./preacher && \
    \
    pip3 --no-cache-dir uninstall -y pip && \
    rm -rf ./preacher ~/.cache && \
    \
    apk --no-cache del .build-deps && \
    \
    preacher-cli --version
