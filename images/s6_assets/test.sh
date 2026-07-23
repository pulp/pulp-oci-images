#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  echo ::group::PIP_LIST
  podman exec pulp bash -c "pip list && pip install pipdeptree<4 && pipdeptree" || true
  echo ::endgroup::
  echo ::group::PODMAN_LOGS
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
             -e PULP_DOMAIN_ENABLED=${domain_enabled} \
             "$1"

  sleep 3  # Wait for the container to start
  podman exec pulp s6-rc -ba list
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
domain_enabled=false

# Configure the GHA host for buildah/skopeo running within the pulp container
# Default range is 165536-231071, 64K long
# sudo usermod --add-subuids 231072-241071 --add-subgid 231072-241071 runner
sudo sed -i "s\runner:165536:65536\runner:165536:75536\g" /etc/subuid /etc/subgid
podman system migrate

mkdir -p settings pulp_storage pgsql containers
echo "CONTENT_ORIGIN='$scheme://localhost:8080'" >> settings/settings.py
echo "ALLOWED_EXPORT_PATHS = ['/tmp']" >> settings/settings.py
echo "ANALYTICS = False" >> settings/settings.py
echo "ALLOWED_CONTENT_CHECKSUMS = ['sha1', 'sha256', 'sha512']" >> settings/settings.py
echo "TASK_DIAGNOSTICS = ['memory']" >> settings/settings.py

if [ "$old_image" != "" ]; then
  start_container_and_wait $old_image
  podman rm -f pulp
fi
if [[ "$image" == "pulp/pulp:ci" ]]; then
  domain_enabled=true
fi
start_container_and_wait $image

source "$BASEDIR/pulp_tests.sh" $scheme
