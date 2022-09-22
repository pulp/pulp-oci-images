#!/bin/bash

database_migrated=false

FILE=/database/migrated
if test -f "$FILE"; then
    echo "Already migrated!"
    exit 0
fi

echo "Checking for database migrations"
while [ $database_migrated = false ]; do
  PULP_CONTENT_ORIGIN=localhost /usr/local/bin/pulpcore-manager showmigrations | grep '\[ \]'
  if [ $? -gt 0 ]; then
    echo "Database migrated!"
    touch $FILE
    database_migrated=true
    cat /database/status
  else
    sleep 5
  fi
done

if [ $database_migrated = false ]; then
  echo "Database not migrated in time, exiting"
  exit 1
else
  exit 0
fi
