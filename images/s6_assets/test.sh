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
             "$1"
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


image=${1:-pulp/pulp:latest}
scheme=${2:-http}
old_image=${3:-""}
if [[ "$scheme" == "http" ]]; then
  port=80
else
  port=443
fi

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
  curl --insecure --fail $scheme://localhost:8080/assets/rest_framework/js/default.js
  grep "127.0.0.1   pulp" /etc/hosts || echo "127.0.0.1   pulp" | sudo tee -a /etc/hosts
  if [ -d pulp-cli ]; then
    cd pulp-cli
    git fetch origin
    git reset --hard origin/main
  else
    git clone --depth=1 https://github.com/pulp/pulp-cli.git
    cd pulp-cli
  fi
  pip install -r test_requirements.txt || pip install --no-build-isolation -r test_requirements.txt
  pulp config create --base-url $scheme://pulp:8080 --username "admin" --password "password" --location tests/cli.toml
  if [[ "$scheme" == "https" ]];then
    podman cp pulp:/etc/pulp/certs/pulp_webserver.crt /tmp/pulp_webserver.crt
    sudo cp /tmp/pulp_webserver.crt /usr/local/share/ca-certificates/pulp_webserver.crt
    # Hack: adding pulp CA to certifi.where()
    CERTIFI=$(python -c 'import certifi; print(certifi.where())')
    cat /usr/local/share/ca-certificates/pulp_webserver.crt | sudo tee -a "$CERTIFI" > /dev/null
  fi
  echo "Setup the signing services"
  # Setup key on the Pulp container
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-KEY-pulp-qe |podman exec -i pulp su pulp -c "cat > /tmp/GPG-KEY-pulp-qe"
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-PRIVATE-KEY-pulp-qe |podman exec -i pulp su pulp -c "gpg --import"
  echo "6EDF301256480B9B801EBA3D05A5E6DA269D9D98:6:" |podman exec -i pulp gpg --import-ownertrust
  # Setup key on the test machine
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-KEY-pulp-qe | cat > /tmp/GPG-KEY-pulp-qe
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-PRIVATE-KEY-pulp-qe | gpg --import
  echo "6EDF301256480B9B801EBA3D05A5E6DA269D9D98:6:" | gpg --import-ownertrust
  echo "Setup ansible signing service"
  podman exec -u pulp -i pulp bash -c "cat > /var/lib/pulp/scripts/sign_detached.sh" < "${PWD}/tests/assets/sign_detached.sh"
  podman exec -u pulp pulp chmod a+rx /var/lib/pulp/scripts/sign_detached.sh
  podman exec -u pulp pulp bash -c "pulpcore-manager add-signing-service --class core:AsciiArmoredDetachedSigningService sign_ansible /var/lib/pulp/scripts/sign_detached.sh 'Pulp QE'"
  echo "Setup deb release signing service"
  podman exec -u pulp -i pulp bash -c "cat > /var/lib/pulp/scripts/sign_deb_release.sh" < "${PWD}/tests/assets/sign_deb_release.sh"
  podman exec -u pulp pulp chmod a+rx /var/lib/pulp/scripts/sign_deb_release.sh
  podman exec -u pulp pulp bash -c "pulpcore-manager add-signing-service --class deb:AptReleaseSigningService sign_deb_release /var/lib/pulp/scripts/sign_deb_release.sh 'Pulp QE'"
  make test
else
  curl --insecure --fail $scheme://localhost:8080/static/galaxy_ng/index.html
fi
