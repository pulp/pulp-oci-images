#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  echo ::group::INFO
  cat ${file}
  echo ::endgroup::
  podman-compose -f ${file} down
}
trap cleanup EXIT

BASEDIR=$(dirname "$0")
image=${1:-pulp-minimal:latest}
web_image=${2:-pulp-web:latest}
file=${3:-compose.yml}

if [[ "$file" == "compose.folders.yml" ]]; then
  # Reuse the folders from the s6 mode tests
  echo "host all all 10.0.0.0/8 trust" | sudo tee -a pgsql/data/pg_hba.conf > /dev/null
  echo "listen_addresses = '*'" | sudo tee -a pgsql/data/postgresql.conf > /dev/null
fi
file="$BASEDIR/$file"

# Change example compose files to use test image name
sed -i "s/pulp-minimal:latest/${image}/g" ${file}
sed -i "s/pulp-web:latest/${web_image}/g" ${file}
id | grep "(root)" || sudo usermod -G root $(whoami)

# Launch podman-compose and test that status endpoint is reachable
podman-compose -f ${file} up -d
podman exec compose_pulp_api_1 /usr/bin/wait_on_database_migrations.sh
for _ in $(seq 20)
do
  if curl --fail http://localhost:8080/pulp/api/v3/status/ > /dev/null 2>&1
  then
    break
  fi
  sleep 3
done
curl --fail http://localhost:8080/pulp/api/v3/status/ | jq