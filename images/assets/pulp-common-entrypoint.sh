#!/bin/bash

# Prevent pip-installed /usr/local/bin/pulp-content from getting run instead of
# our /usr/bin/pulp script.
#
# We still want conatiner users to call pulp-* command names, not paths, so we
# can change our scripts' locations in the future, and call special logic in this
# script based solely on the command name.

# Default value for the migration flag
skip_migrations=false
no_admin_password=false

# Define the usage function
usage() {
    echo "Usage: [pulp-api|pulp-content|pulp-worker|any command] [-s|--skip-migrations]"
    exit 1
}

# Parse command line options using getopt
OPTS=$(getopt -o s --long skip-migrations -n 'pulp-common-entrypoint.sh' -- "$@")

if [ $? != 0 ]; then
    usage
fi

eval set -- "$OPTS"

# Process command line options
while true; do
    case "$1" in
        -sm|--skip-migrations)
            skip_migrations=true
            shift
            ;;
        -np|--no-admin-password)
            no_admin_password=true
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            usage
            ;;
    esac
done

# Get the command argument
command="$1"

# Check if the skip_migrations flag is set
# Check if a command was provided
if [[ -n "$command" && "$command" = "pulp-content" || "$command" = "pulp-api" || "$command" = "pulp-worker" ]]; then

        if [ "$skip_migrations" = true ]; then
            echo "Skipping migrations..."
        fi

        if [ "$no_admin_password" = true ]; then
            echo "Not setting the admin password..."
        fi

        SKIP_MIGRATIONS=skip_migrations NO_ADMIN_PASSWORD=no_admin_password exec "/usr/bin/$command"
else
        exec "$command"
fi
