FROM python:3.7

ENV PREACHER_DIR=/usr/local/preacher

WORKDIR /work

COPY preacher pyproject.toml poetry.lock /usr/local/preacher/
RUN cd /usr/local/preacher && \
    pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev
