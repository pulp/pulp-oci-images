#!/usr/bin/env bash
set -eu

cleanup() {
  echo ::group::INFO
  docker exec pulp bash -c "pip3 list && pip3 install pipdeptree && pipdeptree"
  docker logs pulp
  echo ::endgroup::
  docker stop pulp
}
trap cleanup EXIT


image=${1:-pulp/pulp:latest}
scheme=${2:-http}
if [[ "$scheme" == "http" ]]; then
  port=80
else
  port=443
fi

mkdir settings
echo "CONTENT_ORIGIN='$scheme://localhost:8080'" >> settings/settings.py
docker run --detach \
           --name pulp \
           --publish 8080:$port \
           --volume "/$(pwd)/settings:/etc/pulp:Z" \
           --device /dev/fuse \
           "$image"
sleep 10
for _ in $(seq 20)
do
  sleep 3
  if curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ > /dev/null 2>&1
  then
    break
  fi
done
curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ | jq
