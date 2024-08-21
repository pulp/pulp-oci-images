#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  echo ::group::INFO
  podman exec pulp bash -c "pip3 list && pip3 install pipdeptree && pipdeptree"
  podman logs pulp
  echo ::endgroup::
  podman stop pulp
}
trap cleanup EXIT

# "--security-opt unmask=none" needed on rhel8 for `podman run`, but we only
# ever need to run buildah & skopeo (pulp_container does)
# "--device /dev/net/tun" needed for `podman run`, but we only ever need to run
# buildah & skopeo (pulp_container does)

start_container_and_wait() {

  podman run --detach \
             --publish 8080:$port \
             --name pulp \
             --volume "$(pwd)/settings":/etc/pulp:Z \
             --volume "$(pwd)/pulp_storage":/var/lib/pulp:Z \
             --volume "$(pwd)/pgsql":/var/lib/pgsql:Z \
             --volume "$(pwd)/containers":/var/lib/containers:Z \
             --device /dev/fuse \
             -e PULP_DEFAULT_ADMIN_PASSWORD=password \
             -e PULP_HTTPS=${pulp_https} \
             "$1"

  #echo ::group::VERSIONSPSQL
  #podman exec -it pulp bash 'pg_config --version'
  #podman exec -it pulp bash -c 'psql --version'
  #echo ::endgroup::

  sleep 10
  for _ in $(seq 30)
  do
    sleep 3
    if curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ > /dev/null 2>&1
    then
      # We test it a 2nd time because otherwise there could be an error like:
      # curl: (35) OpenSSL SSL_connect: Connection reset by peer in connection to localhost:8080
      if curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ > /dev/null 2>&1
      then
        break
      fi
    fi
  done
  set -x
  curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ | jq
}

BASEDIR=$(dirname "$0")
image=${1:-pulp/pulp:latest}
scheme=${2:-http}
old_image=${3:-""}
if [[ "$scheme" == "http" ]]; then
  port=80
  pulp_https=false
else
  port=443
  pulp_https=true
fi

# Configure the GHA host for buildah/skopeo running within the pulp container
# Default range is 165536-231071, 64K long
# sudo usermod --add-subuids 231072-241071 --add-subgid 231072-241071 runner
sudo sed -i "s\runner:165536:65536\runner:165536:75536\g" /etc/subuid /etc/subgid
podman system migrate

mkdir -p settings pulp_storage pgsql containers
echo "CONTENT_ORIGIN='$scheme://localhost:8080'" >> settings/settings.py
echo "ALLOWED_EXPORT_PATHS = ['/tmp']" >> settings/settings.py
echo "ORPHAN_PROTECTION_TIME = 0" >> settings/settings.py

if [ "$old_image" != "" ]; then
  start_container_and_wait $old_image
  podman rm -f pulp
fi
start_container_and_wait $image

if [[ ${image} != *"galaxy"* ]];then
  source "$BASEDIR/pulp_tests.sh" $scheme
else
  source "$BASEDIR/galaxy_ng_tests.sh" $scheme
fi
