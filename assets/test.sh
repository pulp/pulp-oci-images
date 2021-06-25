#!/usr/bin/env bash

cleanup() {
  docker stop pulp
}
trap cleanup EXIT


image=${1:-pulp/pulp:latest}

mkdir settings
echo "CONTENT_ORIGIN='http://localhost:8080'" >> settings/settings.py
docker run --detach \
           --name pulp \
           --publish 8080:80 \
           --volume "/$(pwd)/settings:/etc/pulp:Z" \
           --device /dev/fuse \
           "$image"
sleep 10
for _ in $(seq 20)
do
  sleep 3
  if curl --fail http://localhost:8080/pulp/api/v3/status/ > /dev/null 2>&1
  then
    break
  fi
done
curl --fail http://localhost:8080/pulp/api/v3/status/
