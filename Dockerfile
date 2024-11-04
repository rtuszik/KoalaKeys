# syntax = docker/dockerfile:latest

FROM python:3.13.0-alpine3.19 AS base

LABEL maintainer='modem7'

ENV CHEATSHEET_OUTPUT_DIR="/cheatsheets"

COPY --link requirements.txt /

COPY --link /src /src
COPY --link /assets /assets

RUN <<EOF
    set -xe
    mkdir -p /cheatsheets
    chmod -R +x /src/*.py
EOF

RUN --mount=type=cache,id=pip,target=/root/.cache,sharing=locked \
    <<EOF
    set -xe
    python3 -m pip install -U pip
    python3 -m pip install -Ur requirements.txt
EOF

VOLUME /cheatsheet

ENTRYPOINT ["python", "src/generate_cheatsheet.py"]
