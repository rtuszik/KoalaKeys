#!/usr/bin/env bash

docker compose down
rm -rf ./output/*

# docker buildx build --platform linux/amd64,linux/arm64 --load --tag tobiashochguertel/koala-keys .
docker buildx build --platform linux/amd64,linux/arm64 --push --load --tag tobiashochguertel/koala-keys .
