#!/bin/bash -eu

/usr/bin/wait_on_postgres.py
/usr/bin/wait_on_database_migrations.sh

if [ -n "${PULP_SIGNING_KEY_FINGERPRINT}" ]; then
  /usr/local/bin/pulpcore-manager add-signing-service "${COLLECTION_SIGNING_SERVICE}" /var/lib/pulp/scripts/collection_sign.sh "${PULP_SIGNING_KEY_FINGERPRINT}"
  /usr/local/bin/pulpcore-manager add-signing-service "${CONTAINER_SIGNING_SERVICE}" /var/lib/pulp/scripts/container_sign.sh "${PULP_SIGNING_KEY_FINGERPRINT}" --class container:ManifestSigningService
fi
