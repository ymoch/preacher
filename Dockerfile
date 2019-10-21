FROM python:3.7-alpine

WORKDIR /work

COPY README.md pyproject.toml poetry.lock /usr/local/preacher/
COPY preacher /usr/local/preacher/preacher
RUN apk --no-cache add libc-dev libxml2-dev libxslt-dev libtool autoconf automake make gcc && \
    pip --no-cache-dir install poetry==0.12.11 && \
    cd /usr/local/preacher && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev && \
    pip --no-cache-dir uninstall --yes poetry && \
    pip install . && \
    rm -rf ~/.cache && \
    apk --no-cache del libtool autoconf automake make gcc