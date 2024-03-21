# Migrate from pulp_installer to a multi-process container

## Overview

These instructions will migrate you from a [pulp_installer deployment](https://docs.pulpproject.org/pulp_installer/) to a [multi-process container deployment](multi-process-images).

The same host will be running Pulp, but in a container now.

All of pulp_installer 3.23's supported distros are documented, but instructions will have extra steps depending upon the PostgreSQL version (the container runs PostgreSQL 13). These steps are all listed in the instructions per distro, but here is an overview:

| Distro | PostgreSQL Version | Extra Steps |
| ------ | ------------------ | ------------- |
| Debian 11 | 13 | |
| EL7 | 10 | Dump and restore the database |
| EL8 | 10 | Dump and restore the database |
| EL9 | 13 | |
| Fedora 33 | 12 | Starting the container will take longer the 1st time |
| Fedora 34 | 13 | |
| Fedora 35 | 13 | |
| Fedora 36 | 14 | PostgreSQL must remain running on the host |
| Ubuntu 22.04 | 14 | PostgreSQL must remain running on the host |

## Limitations

1. All of your existing installed plugins must be installed in the multi-process container image. See the list of installed plugins [here.](multi-process-images#available-images)

## Prerequisites

1. Either [podman](https://podman.io/getting-started/installation) or
[docker](https://docs.docker.com/engine/install/)/[moby-engine](https://mobyproject.org/)
must be installed on the host.
2. If you are running podman in rootless mode (which is recommended for security), make sure your user account has subuid's and subgid's (the default behavior for new acconts on many Linux distros.) See [this guide](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md#etcsubuid-and-etcsubgid-configuration) to verify / set this up.
3. If you are running docker/moby-engine, either the user account is in the docker group, or you preface `docker` commands with `sudo`.

## Assumptions

1. The directory you run the commands in is one where you want the Pulp data and configuration directories to reside under. You can actually let them reside in their current (pulp_installer defaulted or specified) directories on the system if you'd prefer, just specify the absolute folder paths in the commands below, and do not run the move commands.
2. If you are running rootless podman, you are running `podman` commands from the account that the container will run under. 
3. sudo commands are run under an account that actually has sudo. This need not necessarily be the rootless podman account, but if it isn't, substitute `$USER:$(id -gn)` with the user and primary group (seperated by a colon) of the rootless podman account.
4. If you are running docker, substitue `docker` for `podman` in the commands.

## Step-By-Step-Guide

### Disable and stop the Pulp service

```
sudo systemctl disable --now pulpcore
```

### Configure PostgreSQL to listen on all network interfaces (Fedora 36 and Ubuntu 22.04 only)

This is necessary for container networks to access PostgreSQL.

Ensure this line is in `/var/lib/pgsql/data/pg_hba.conf` (Fedora 36) / `/etc/postgresql/14/main/pg_hba.conf` (Ubuntu 22.04):
```
host all all 0.0.0.0/0 md5
```

Ensure this line is in `/var/lib/pgsql/data/postgresql.conf` (Fedora 36) / `/etc/postgresql/14/main/postgresql.conf` (Ubuntu 22.04):
```
listen_addresses = '*'
```

Run:
```
sudo systemctl restart postgresql
```

### Dump the PostgreSQL database (EL7 and EL8 only)

```
sudo -u postgres pg_dumpall > /tmp/dump.sql
```

Verify that this command outputs "0", which indicates that the dump was successful.

```
echo $?
```

```
sudo mv /tmp/dump.sql /var/lib/pgsql
```

### Disable/restart the third-party services

On Fedora 36:
```
sudo systemctl disable --now nginx redis
```
On Ubuntu 22.04:
```
sudo systemctl disable --now nginx redis-server
```
On on EL, or Fedora prior to 36:
```
sudo systemctl disable --now postgresql nginx redis
```
On Debian 11:
```
sudo systemctl disable --now postgresql nginx redis-server
```


### Manage the Pulp storage directory

1st, move the directory:

```
sudo mv /var/lib/pulp/ pulp_storage
```

Next change ownership of the directory:

If running rootless podman:
```
sudo chown -R $USER:$(id -gn) pulp_storage
podman unshare chown -R 700:700 pulp_storage
```

If running podman as root, or docker:
```
sudo chown -R 700:700 pulp_storage
```

### Manage the Pulp configuration directory

1st, move the directory:
```
sudo mv /etc/pulp settings
```

Next change ownership of the directory:

If running rootless podman:
```
sudo chown -R $USER:$(id -gn) settings
podman unshare chown -R 700:700 settings
```
If running podman as root, or docker:
```
sudo chown -R 700:700 settings
```

### Configure Pulp to talk to the database (Fedora 36 and Ubuntu 22.04 only)

If running podman, modify `settings/settings.py` so that "DATABASE" includes:
```
'HOST': 'host.containers.internal'
```
An example of what the line will look like:
```
DATABASES = {'default': {'HOST': 'host.containers.internal', 'ENGINE': 'django.db.backends.postgresql', 'NAME': 'pulp', 'USER': 'pulp', 'PASSWORD': 'pulp'}}
```

If running docker, modify `settings/settings.py` so that "DATABASE" includes:
```
'HOST': 'host.docker.internal'
```
An example of what the line will look like:
```
DATABASES = {'default': {'HOST': 'host.docker.internal', 'ENGINE': 'django.db.backends.postgresql', 'NAME': 'pulp', 'USER': 'pulp', 'PASSWORD': 'pulp'}}
```

### Manage the PostgreSQL data directory (EL, Fedora prior to 36, and Debian 11 only)

1st, move the directory:

If on EL, or Fedora prior to 36
```
sudo mv /var/lib/pgsql pgsql
```
If on Debian 11:
```
sudo mv /var/lib/postgresql/13 pgsql
sudo mv pgsql/main pgsql/data
```
If on EL7 or EL8:
```
sudo mv pgsql/data pgsql/data_old
```

Next, if on Debian 11, move the config files:
```
sudo mv /etc/postgresql/13/main/*.conf /etc/postgresql/13/main/conf.d/ pgsql/data/
```

Next change ownership of the directory:

If running rootless podman:
```
sudo chown -R $USER:$(id -gn) pgsql
podman unshare chown -R 26:26 pgsql
```
If running podman as root, or docker:
```
sudo chown -R 26:26 pgsql
```

### Configure Postgres to be compatible with the EL8-based container (Debian 11 only)

Backup `pgsql/data/postgresql.conf` before you modify it:
```
sudo cp pgsql/data/postgresql.conf pgsql/data/postgresql.conf.old
```

Next, comment out the following lines in `pgsql/data/postgresql.conf`:
```
data_directory
hba_file
ident_file
external_pid_file
unix_socket_directories
ssl
ssl_cert_file
ssl_key_file
cluster_name
stats_temp_directory
```

### Create an empty containers directory

We do not bother to move `/var/lib/containers` because it is only ever used for temporary files by pulp_container, and may be used on the host for other purposes (like running podman):

```
mkdir containers
```

### Configure the system to allow listening on low ports (rootless podman only)

The default ports for pulp_installer were 443 (with https, the default) or 80 (without https).

If you are running rootless podman, and you wish to preserve the low port (anything under 1024)
that Pulp listens on (recommended to avoid reconfiguring clients),
you must configure the system to permit unprivileged
processes listening on low ports.

Assuming the port is 443, run the following command:
```
sudo sysctl net.ipv4.ip_unprivileged_port_start=443
echo "net.ipv4.ip_unprivileged_port_start=443" | sudo tee /etc/sysctl.d/10-low_ports.conf
```

### Restore the database (EL7 or EL8 only)

Run the container with the normal [command](site:/pulp-oci-images/docs/admin/guides/deploy-multi-process-images/#starting-the-container), but with `-it` instead of `-detach`, and with `/bin/bash` as the specified command. We also omit the "--publish 8080:80"
```
podman run -it \
           --name pulp \
           --volume "$(pwd)/settings":/etc/pulp:Z \
           --volume "$(pwd)/pulp_storage":/var/lib/pulp:Z \
           --volume "$(pwd)/pgsql":/var/lib/pgsql:Z \
           --volume "$(pwd)/containers":/var/lib/containers:Z \
           --device /dev/fuse \
           pulp/pulp \
           /bin/bash
```

You will now be running commands in the container:
```
su postgres -c "initdb -E UTF8 --locale=C.UTF-8 --pgdata=/var/lib/pgsql/data"
su postgres -c "pg_ctl start -D /var/lib/pgsql/data"
su postgres -c "psql -d postgres -f /var/lib/pgsql/dump.sql"
```

Verify that this next command outputs "0" to indicate that the database restore was successful.
```
echo $?
```

```
su postgres -c "pg_ctl stop -D /var/lib/pgsql/data"
```

Now exit the container:
```
exit
```

Now delete the container (but not the data directories):
```
podman rm pulp
```

### Run the container like normal.

Run the container with the normal [command](site:/pulp-oci-images/docs/admin/guides/deploy-multi-process-images/#starting-the-container).

There are 2 migration-specific exceptions to the instructions on that page.

The 1st exception is the port that Pulp listens on.

https is the default for pulp_installer, so see the https instructions on [that page](site:/pulp-oci-images/docs/admin/guides/deploy-multi-process-images/#starting-the-container) if you wish to continue running https. However, instead of specifying `--publish 8080:443` or `--publish 80:80`, specify `--publish 443:443`. This will keep Pulp listening on port 443, thus avoiding the need to reconfigure clients. This will be part of your new normal command.

If you are not running https, the command below has been modified to listen on port 80 rather than
8080. `--publish 8080:80` has been replaced with `--publish 80:80`. This will be part of your new
normal command.

The 2nd possible exception is for the pgsql directory and networking.

If you are running podman on Fedora 36 or Ubuntu 22.04, leave out `--volume "$(pwd)/pgsql":/var/lib/pgsql:Z`, and add `--network slirp4netns:allow_host_loopback=true,cidr=10.0.100.0/24`. This will be part of your new normal command.

If you are running docker on Fedora 36 or Ubuntu 22.04, leave out `--volume "$(pwd)/pgsql":/var/lib/pgsql:Z`, and add `--add-host=host.docker.internal:host-gateway`. This will be part of your new normal command.

```
podman run --detach \
             --publish 80:80 \
             --name pulp \
             --volume "$(pwd)/settings":/etc/pulp:Z \
             --volume "$(pwd)/pulp_storage":/var/lib/pulp:Z \
             --volume "$(pwd)/pgsql":/var/lib/pgsql:Z \
             --volume "$(pwd)/containers":/var/lib/containers:Z \
             --device /dev/fuse \
             pulp/pulp
```

It is recommended to view the container logs:
```
podman logs -f pulp
```

If you are running Fedora 33, startup will take longer than usual as the database is migrated from PostgreSQL 12 to 13. This is done automatically using the image's built-in upgrade logic.
