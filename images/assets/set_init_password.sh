#!/bin/bash -eu

/usr/bin/wait_on_postgres.py
/usr/bin/wait_on_database_migrations.sh

if [[ -n "$PULP_DEFAULT_ADMIN_PASSWORD" ]]
then
  PASSWORD_SET=$(/usr/local/bin/pulpcore-manager shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username=\"admin\").exists())")
  if [ "$PASSWORD_SET" = "False" ]
  then
    /usr/local/bin/pulpcore-manager reset-admin-password --password "${PULP_DEFAULT_ADMIN_PASSWORD}"
  fi
else
  ADMIN_PASSWORD_FILE=/etc/pulp/pulp-admin-password
  if [[ -f "$ADMIN_PASSWORD_FILE" ]]; then
     echo "pulp admin can be initialized."
     PULP_ADMIN_PASSWORD=$(cat $ADMIN_PASSWORD_FILE)
  fi

  if [ -n "${PULP_ADMIN_PASSWORD}" ]; then
      /usr/local/bin/pulpcore-manager reset-admin-password --password "${PULP_ADMIN_PASSWORD}"
  fi
fi
set -x

