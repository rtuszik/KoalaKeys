# syntax = docker/dockerfile:latest

FROM python:3.13.0-alpine3.19 AS base

LABEL maintainer='rtuszik'

ENV CHEATSHEET_OUTPUT_DIR="/cheatsheets"

COPY --link requirements.txt /

RUN --mount=type=cache,id=pip,target=/root/.cache,sharing=locked \
    <<EOF
    set -xe
    mkdir -p /cheatsheets
    python3 -m pip install -U pip
    python3 -m pip install -Ur requirements.txt
EOF

COPY --chmod=744 --link /src /src
COPY --chmod=744 --link /assets /assets

VOLUME /cheatsheet

ENTRYPOINT ["python", "src/generate_cheatsheet.py"]
