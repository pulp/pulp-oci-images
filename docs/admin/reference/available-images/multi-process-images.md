# Multi-Process Images

These images are also known as "Single Container", or "Pulp in One Container".

Each image runs all 3 Pulp services (pulp-api, pulp-content and pulp-worker),
as well as Pulp's third-party services (nginx, postgresql and redis),
in one single container.

## System Requirements

Either [podman](https://podman.io/getting-started/installation) or
[docker](https://docs.docker.com/engine/install/)/[moby-engine](https://mobyproject.org/)
must be installed.

Podman has been tested at versions as low as 1.6.4, which is available on CentOS/RHEL 7 and later.

## Available images

### pulp

This image contains [Pulp](https://github.com/pulp/pulpcore) and the following plugins currently:

- [pulp_ansible](site:pulp_ansible)
- [pulp-certguard](site:pulp_certguard)
- [pulp_container](site:pulp_container)
- [pulp_deb](site:pulp_deb)
- [pulp_file](site:pulp_file)
- [pulp_maven](site:pulp_maven)
- [pulp_python](site:pulp_python)
- [pulp_rpm](site:pulp_rpm)
- [pulp_ostree](site:pulp_ostree)

This image can also function the same as the single-process image `pulp-minimal`.
See the [Single-Process Images](../single-process-images/) page for usage.

#### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `nightly`: Built nightly, With master/main branches of each plugin. Also built with several
  additional plugins that are not GA yet.
- `3.y`:  Pulpcore 3.y version and its compatible plugins. Built whenever there is a z-release.

[Browse available tags](https://hub.docker.com/r/pulp/pulp/tags)

#### Discontinued tags

- `https`: These were built nightly, with latest released version of each plugin. Nginx webserver ran with SSL/TLS. Now, use `stable` instead with `-e PULP_HTTPS=true`.
- `3.y-https`:  Pulpcore 3.y version and its compatible plugins. These were built whenever there is a z-release.
  Nginx webserver ran with SSL/TLS. Now, use `3.y` instead with `-e PULP_HTTPS=true`.

### galaxy

This image contains Ansible [Galaxy](https://github.com/ansible/galaxy_ng).

This image can also function the same as the single-process image `galaxy-minimal`.
See the [Single-Process Images](../single-process-images/) page for usage.

Note that this name `galaxy` used to be for single-process images. Version tags `4.6.3` and earlier
are single-process rather than multi-process.

#### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.

[Browse available tags](https://hub.docker.com/r/pulp/galaxy/tags)

#### Discontinued tags

- `https`: These were built nightly, with latest released version of each plugin. Nginx webserver ran with SSL/TLS. Now, use `stable` instead with `-e PULP_HTTPS=true`.

## Quickstart

### Galaxy Quickstart

The galaxy base image includes a default settings.py and can be configured using environment variables. This image can be configured with the following two environment variables:

- `GALAXY_HOSTNAME`: publicly accessible hostname that the API and content app will run on.
- `GALAXY_PORT`: public port that the API and content app will run on.

The galaxy image can also be run just like any of the other multi process pulp images by mounting a custom settings.py file, however this setup provides an easy, out of the box configuration for running galaxy.

#### Examples

Run galaxy on localhost:

```
$ podman run -p 8080:80 ghcr.io/pulp/galaxy:latest
```

Run galaxy on localhost with https:

```
$ podman run -p 443:443 -e "PULP_HTTPS=true" -e "GALAXY_PORT=443" ghcr.io/pulp/galaxy:latest
```

Run galaxy from a server with https:

```
$ podman run -p 443:443 -e "PULP_HTTPS=true" -e "GALAXY_PORT=443" -e "GALAXY_HOSTNAME=192.168.0.100" ghcr.io/pulp/galaxy:latest
```

Modify the system settings to allow for uploads without approval:

```
$ podman run -p 8080:80 -e "PULP_GALAXY_REQUIRE_CONTENT_APPROVAL=false" ghcr.io/pulp/galaxy:latest
```

Mount the storage directories for persistent data and https:

NOTE: don't mount volumes to `/etc/pulp/` as you would with the vanilla pulp images, as this will
override the default settings.py file.

```
$ podman run --detach \
             --publish 443:443 \
             --name pulp \
             -e "GALAXY_HOSTNAME=my.galaxy.host.example.com" \
             -e "PULP_HTTPS=true" \
             -e "GALAXY_PORT=443" \
             --volume "$(pwd)/settings/certs":/etc/pulp/certs:Z \
             --volume "$(pwd)/pulp_storage":/var/lib/pulp:Z \
             --volume "$(pwd)/pgsql":/var/lib/pgsql:Z \
             --volume "$(pwd)/containers":/var/lib/containers:Z \
             --device /dev/fuse \
             ghcr.io/pulp/galaxy:latest
```

Once your containers are running see "Reset the Admin Password" section to set up your admin user.

### Create the Directories and Settings

1st, create the directories for storage/configuration, and create the `settings.py` file:

```
$ mkdir -p settings/certs pulp_storage pgsql containers
$ echo "CONTENT_ORIGIN='http://$(hostname):8080'
ANSIBLE_API_HOSTNAME='http://$(hostname):8080'
ANSIBLE_CONTENT_HOSTNAME='http://$(hostname):8080/pulp/content'
CACHE_ENABLED=True" >> settings/settings.py
```

* For a complete list of available settings for `settings.py`,
  see [the Pulpcore Settings](site:pulpcore/docs/admin/reference/settings/).

* These 4 directories `settings pulp_storage pgsql containers` must be preserved. `settings` has
  your settings, generated certificates, and generated database encrypted fields key. The
  `pulp_storage pgsql containers` are the application data.

### Starting the Container

For systems with SELinux enabled, use the following command to start Pulp:

```
$ podman run --detach \
             --publish 8080:80 \
             --name pulp \
             --volume "$(pwd)/settings":/etc/pulp:Z \
             --volume "$(pwd)/pulp_storage":/var/lib/pulp:Z \
             --volume "$(pwd)/pgsql":/var/lib/pgsql:Z \
             --volume "$(pwd)/containers":/var/lib/containers:Z \
             --device /dev/fuse \
             pulp/pulp
```

For systems with SELinux disabled, use the following command to start Pulp:

```
$ podman run --detach \
             --publish 8080:80 \
             --name pulp \
             --volume "$(pwd)/settings":/etc/pulp \
             --volume "$(pwd)/pulp_storage":/var/lib/pulp \
             --volume "$(pwd)/pgsql":/var/lib/pgsql \
             --volume "$(pwd)/containers":/var/lib/containers \
             --device /dev/fuse \
             pulp/pulp
```

* For Docker systems, use the last 2 command, but substitute `docker` for `podman`.

* These examples use the image `pulp`  with the tag `stable` (AKA `latest`). To use an alternative image and tag like `pulp:3.21`, substitute `pulp/pulp` with `pulp/pulp:3.21`.

* To use https instead of http, add `-e PULP_HTTPS=true` Also change `--publish 8080:80` to `--publish 8080:443`

### Reset the Admin Password

Now, reset the admin user’s password.

```
$ podman exec -it pulp bash -c 'pulpcore-manager reset-admin-password'
Please enter new password for user "admin":
Please enter new password for user "admin" again:
Successfully set password for "admin" user.
```

* For Docker systems, substitute `docker` for `podman`.


### Test Access

At this point, both the REST API and the content app are available on your host’s port 8080. Try hitting the pulp status endpoint to confirm:

```
curl localhost:8080/pulp/api/v3/status/
```

### What to do after the Quickstart

To start working with Pulp, check out the [Workflows and Use Cases](https://github.com/pulp/pulpcore/issues/5593)
and explore individual Content Plugins documentation.

If you are unsure what to pick first, try Python's
[Setup Your Own Pypi](site:pulp_python/docs/user/guides/pypi/) or RPM's
[Sync and Publish](site:pulp_rpm/docs/user/tutorials/create_sync_publish/).

We recommend using [pulp-cli](https://github.com/pulp/pulp-cli) to interact with Pulp. If you have Python 3 installed on the host OS, you can run these commands to get started:

```
pip install pulp-cli[pygments]
pulp config create --username admin --base-url http://localhost:8080 --password <admin password>
```

## Advanced Usage Instructions

### Available Environment Variables

The following environment variables configure the container's behavior.

* `PULP_WORKERS` An integer that specifies the number of worker processes (which perform syncing, importing of content, and other asynchronous operations that require resource locking.) Defaults to 2.

* `PULP_API_WORKERS` A positive integer that specifies the number of [gunicorn worker processes](https://docs.gunicorn.org/en/stable/settings.html#workers) for handling Pulp API requests. Default to 2.

* `PULP_CONTENT_WORKERS` A positive integer that specifies the number of [gunicorn worker processes](https://docs.gunicorn.org/en/stable/settings.html#workers) for handling Pulp Content requests. Default to 2.

* `PULP_GUNICORN_RELOAD` Set to "true" (all lowercase) for the pulpcore-api gunicorn process to be started with ["--reload"](https://docs.gunicorn.org/en/latest/settings.html?highlight=reload#reload). Intended for developers.

* `PULP_GUNICORN_TIMEOUT` A positive integer that specifies the [timeout for gunicorn process](https://docs.gunicorn.org/en/stable/settings.html#timeout). Default to 90.

* `PULP_API_WORKERS_MAX_REQUESTS` The maximum number of requests a worker will process before restarting API workers. If this is set to zero (the default) then the automatic worker restarts are disabled. NOTE: Only supported for pulpcore >= 3.41.0

* `PULP_API_WORKERS_MAX_REQUESTS_JITTER` The maximum jitter to add to the max_requests setting for API workers. NOTE: Only supported for pulpcore >= 3.41.0

* `PULP_CONTENT_WORKERS_MAX_REQUESTS` The maximum number of requests a worker will process before restarting Content workers. If this is set to zero (the default) then the automatic worker restarts are disabled. NOTE: Only supported for pulpcore >= 3.41.0

* `PULP_CONTENT_WORKERS_MAX_REQUESTS_JITTER` The maximum jitter to add to the max_requests setting for Content workers. NOTE: Only supported for pulpcore >= 3.41.0

To add one of them, modify the command you use to start pulp to include syntax like the following at the beginning: Instead of `podman run`, specify `podman run -e PULP_WORKERS=4 -e PULP_GUNICORN_TIMEOUT=30 -e PULP_API_WORKERS_MAX_REQUESTS=1000 -e PULP_API_WORKERS_MAX_REQUESTS_JITTER=50 ...`

### Adding Signing Services

Administrators can add signing services to Pulp using the command line tools. Users may then associate the signing services with repositories that support content signing.
See [Signing Services](site:pulp-oci-images/docs/admin/guides/configure-signing-service/) documentation for more information.

### Certificates and Keys

Follow the instructions from [certificates](site:pulp-oci-images/docs/admin/guides/configure-certificates/) documentation for more information about how to configure custom certificates.

Check [database encryption](site:pulp-oci-images/docs/admin/guides/configure-database-encryption/) documentation for more information about the key to encrypt sensitive fields in the database.

### Command to specify

To run all the services, you do not need to specify a container command ("CMD"). The default CMD is:

- **/init** - The [s6 service manager](https://github.com/just-containers/s6-overlay) that runs all the services.

## Upgrading

To upgrade to a newer version of Pulp, such as the `latest` image which is published every night, start by running:

```
podman stop pulp
podman rm pulp
```

Then update the image in the local podman/docker cache:

```
podman pull pulp/pulp
```

Then repeat the original command in [Starting the Container](#starting-the-container) (with any customizations you added to it.)


## Known Issues

### NFS or SSHFS

When using rootless podman, you cannot create the directories (settings pulp_storage pgsql containers) on [NFS](https://github.com/containers/podman/blob/master/rootless.md#shortcomings-of-rootless-podman), SSHFS, or certain other non-standard filesystems.

### Podman on CentOS 7

When using on CentOS 7, container-selinux has a
limitation. [1](https://github.com/containers/podman/issues/9513)
[2](https://github.com/containers/podman/issues/6414)
SELinux denials will prevent Pulp from running. To
overcome it, you must do one of the following:

* Run the container with "--privileged"
* Run the container as root
* Disable SELinux

Additionally, you will likely run into a limit on the number of open files (ulimit) in the
container.
One way to overcome this is to add `DefaultLimitNOFILE=65536` to `/etc/systemd/system.conf`.

### Docker on CentOS 7

While using the version of Docker that is provided with CentOS 7, there are known issues that cause the following errors to occur:

* When starting the container:

  `FATAL:  could not create lock file "/var/run/postgresql/.s.PGSQL.5432.lock": No such file or directory`

* (If the preceding error is worked around,) when executing `docker exec -it pulp bash -c 'pulpcore-manager reset-admin-password'`:

  ```
  psycopg2.OperationalError: could not connect to server: No such file or directory
        Is the server running locally and accepting
        connections on Unix domain socket "/var/run/postgresql/.s.PGSQL.5432"?
  ```

* Pulp tasks are stuck in `waiting` status, and executing `docker exec -it pulp bash -c 'rq info'` returns `0 workers`:

  ```
  1 queues, 2 jobs total

  0 workers, 1 queues
  ```

The version of Docker that is provided with CentOS 7 mounts `tmpfs` on `/run`. The Pulp Container recipe uses `/var/run`, which is a symlink to `/run`, and expects its contents to be available at container run time. You can work around this by specifying an additional `/run` volume, which suppresses this behavior of the Docker runtime. Docker will copy the image's contents to that volume and the container should start as expected.

The `/run` volume will need to contain a `postgresql` directory (with permissions that the container's postgresql can write to) and a separate `pulpcore-*` directory for the rq manager and its workers to start:

```console
$ mkdir -p settings pulp_storage pgsql containers run/postgresql run/pulpcore-{resource-manager,worker-{1,2}}
$ chmod a+w run/postgresql
```

### Upgrading from ``pulp/pulp-fedora31`` image

The ``pulp/pulp-fedora31`` container vendored PostgreSQL 11. The ``pulp/pulp`` image vendors PostgreSQL 13, and only automatically upgrades from PostgreSQL 12. To upgrade the database from 11 to 12, refer to [PostgreSQL documentation](https://www.postgresql.org/docs/12/upgrading.html).


## Build instructions

The Container file and all other assets used to build the container image are available on [GitHub](https://github.com/pulp/pulp-oci-images).

```bash
$ <docker build | buildah bud> --file images/Containerfile.core.base --tag pulp/base:latest .
$ <docker build | buildah bud> --file images/pulp_ci_centos/Containerfile --tag pulp/pulp-ci-centos9:latest .
$ <docker build | buildah bud> --file images/pulp/stable/Containerfile --tag pulp/pulp:latest .
$ <docker build | buildah bud> --file images/galaxy/stable/Containerfile --tag pulp/galaxy:latest
```

### Specifying versions

By default, containers get built using the latest version of each Pulp component. If you want to
specify a version of a particular component, you can do so with args:

```bash
$ <docker build | buildah bud> --build-arg PULPCORE_VERSION="==3.5.0" --file images/pulp/Containerfile
$ <docker build | buildah bud> --build-arg PULP_FILE_VERSION=">=1.0.0" --file images/pulp/Containerfile
```

## Debugging instructions

### Debugging the services

To debug the services and actually see their output, after stating the container run:
```bash
docker logs -f pulp
```
You will then see the output of the commands and echo statements from the service scripts on the
console.

Afterwards, to see what services started successfully:
```bash
s6-rc -a list
```
And what services failed to start:
```bash
s6-rc -da list
```
To attempt to manually start a failed service:
```bash
s6-rc change servicename
```
