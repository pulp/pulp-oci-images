#!/usr/bin/env bash
set -euo pipefail

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
echo "ALLOWED_EXPORT_PATHS = ['/tmp']" >> settings/settings.py
echo "ORPHAN_PROTECTION_TIME = 0" >> settings/settings.py
# pulp_rpm < 3.25 requires sha1 in allowed checksums
echo "ALLOWED_CONTENT_CHECKSUMS = ['sha1', 'sha256', 'sha512']" >> settings/settings.py

docker run --detach \
           --name pulp \
           --publish 8080:$port \
           --volume "/$(pwd)/settings:/etc/pulp:Z" \
           --device /dev/fuse \
           "$image"
sleep 10
for _ in $(seq 30)
do
  sleep 3
  if curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ > /dev/null 2>&1
  then
    break
  fi
done
curl --insecure --fail $scheme://localhost:8080/pulp/api/v3/status/ | jq

echo "Installing Pulp-CLI"
pip install pulp-cli

# Retreive installed pulp-cli version
PULP_CLI_VERSION=$(python3 -c \
  'import importlib.metadata; \
   from packaging.version import Version; \
   print(Version(importlib.metadata.version("pulp-cli")))')

if [[ ${image} != *"galaxy"* ]];then
  docker exec pulp pulpcore-manager reset-admin-password --password password
  echo 127.0.0.1   pulp | sudo tee -a /etc/hosts
  git clone --depth=1 https://github.com/pulp/pulp-cli.git -b "${PULP_CLI_VERSION}"
  cd pulp-cli
  pip install -r test_requirements.txt || pip install --no-build-isolation -r test_requirements.txt
  pulp config create --base-url $scheme://pulp:8080 --username "admin" --password "password" --no-verify-ssl --location tests/cli.toml
  if [[ "$scheme" == "https" ]];then
    sudo docker cp pulp:/etc/pulp/certs/pulp_webserver.crt /usr/local/share/ca-certificates/pulp_webserver.crt
    # Hack: adding pulp CA to certifi.where()
    CERTIFI=$(python -c 'import certifi; print(certifi.where())')
    cat /usr/local/share/ca-certificates/pulp_webserver.crt | sudo tee -a "$CERTIFI" > /dev/null
  fi
  echo "Setup the signing services"
  # Setup key on the Pulp container
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-KEY-fixture-signing |docker exec -i pulp bash -c "cat > /tmp/GPG-KEY-fixture-signing"
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-PRIVATE-KEY-fixture-signing |docker exec -i pulp gpg --import
  echo "0C1A894EBB86AFAE218424CADDEF3019C2D4A8CF:6:" |docker exec -i pulp gpg --import-ownertrust
  # Setup key on the test machine
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-KEY-fixture-signing | cat > /tmp/GPG-KEY-pulp-qe
  curl -L https://github.com/pulp/pulp-fixtures/raw/master/common/GPG-PRIVATE-KEY-fixture-signing | gpg --import
  echo "0C1A894EBB86AFAE218424CADDEF3019C2D4A8CF:6:" | gpg --import-ownertrust
  echo "Setup ansible signing service"
  docker exec -i pulp bash -c "cat > /root/sign_detached.sh" < "${PWD}/tests/assets/sign_detached.sh"
  docker exec pulp chmod a+x /root/sign_detached.sh
  docker exec pulp bash -c "pulpcore-manager add-signing-service --class core:AsciiArmoredDetachedSigningService sign_ansible /root/sign_detached.sh 'pulp-fixture-signing-key'"
  echo "Setup deb release signing service"
  docker exec -i pulp bash -c "cat > /root/sign_deb_release.sh" < "${PWD}/tests/assets/sign_deb_release.sh"
  docker exec pulp chmod a+x /root/sign_deb_release.sh
  docker exec pulp bash -c "pulpcore-manager add-signing-service --class deb:AptReleaseSigningService sign_deb_release /root/sign_deb_release.sh 'pulp-fixture-signing-key'"
  make test
fi
