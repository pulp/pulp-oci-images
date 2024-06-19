# Quickstart

Here are some common deployment scenarios, each with a guide on how to get started further below.

1. To deploy to [K8s](https://kubernetes.io/),
   [EKS](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html), or
   [Openshift](https://www.redhat.com/en/technologies/cloud-computing/openshift) use the
   [Pulp Operator](https://docs.pulpproject.org/pulp_operator/quickstart/) which was specially built
   for this purpose.
2. Local [deployment via a single container](#single-container). This is for small deployments that
   don't need to scale beyond the hardware available to a single container.
3. Local [deployment with multiple containers using podman or docker compose](
   #podman-or-docker-compose).

In all cases, after deployment see
[what to do after the quickstart](#what-to-do-after-the-quickstart) to start using your installation.


## Single Container

This deployment is a 2-step process:
1. [Creating persistent directories and settings](#create-the-directories-and-settings).
2. [Starting the container](#starting-the-container)


### Create the Directories and Settings

1st, create the directories for storage/configuration, and create the `settings.py` file:

```
$ mkdir -p settings/certs pulp_storage pgsql containers
$ echo "CONTENT_ORIGIN='http://$(hostname):8080'" >> settings/settings.py
```

* For a complete list of available settings for `settings.py`, see [the Pulpcore Settings](https://docs.pulpproject.org/pulpcore/configuration/settings.html).

* These 4 directories `settings`, `pulp_storage`, `pgsql`, `containers` must be preserved. `settings`
  has your settings, generated certificates, and generated database encrypted fields key. The
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


## Podman or Docker Compose

Everything under the assets directory will be mounted into the container.
Please modify the files as needed.

[podman-compose installation docs](https://github.com/containers/podman-compose#installation).

### Running with podman

```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
podman-compose up
```

### Running with docker and scaling

```shell
pip install docker-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
docker-compose up
docker-compose scale pulp_api=4 pulp_content=4
```

### Running with podman and using existing directories for data
```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
mkdir ../../pgsql ../../pulp_storage
podman unshare chown 700:700 ../../pulp_storage
podman-compose -f docker-compose.folders.yml up
```

### Running with docker and using existing directories for data
```shell
pip install podman-compose
git clone git@github.com:pulp/pulp-oci-images.git
cd images/compose
mkdir ../../pgsql ../../pulp_storage
sudo chown 700:700 ../../pulp_storage
podman-compose -f docker-compose.folders.yml up
```



## What to do after the Quickstart

Typically after installation do these steps:

1. [Reset the admin password](#reset-the-admin-password).
2. [Test access](#test-access).
3. [Install the pulp-cli](#install-the-pulp-cli).
4. [Try out a workflow](#try-out-a-workflow)!


### Reset the Admin Password

Now, reset the admin user’s password.

```
$ podman exec -it pulp bash -c 'pulpcore-manager reset-admin-password'
Please enter new password for user "admin":
Please enter new password for user "admin" again:
Successfully set password for "admin" user.
```

> **Note**: For Docker systems, substitute `docker` for `podman`.


### Test Access

At this point, both the REST API and the content app are available on your host’s port 8080. Try hitting the pulp status endpoint to confirm:

```
curl localhost:8080/pulp/api/v3/status/
```


### Install the pulp-cli

We recommend using [pulp-cli](https://github.com/pulp/pulp-cli) to interact with Pulp. If you have Python 3 installed on the host OS, you can run these commands to get started:

```
pip install pulp-cli[pygments]
pulp config create --username admin --base-url http://localhost:8080 --password <admin password>
```


### Try out a workflow

To start working with Pulp, check out the [Workflows and Use Cases](https://docs.pulpproject.org/workflows/index.html). For individual plugin documentation, see [Pulp 3 Content Plugin Documentation](https://pulpproject.org/docs/#pulp-3-content-plugin-documentation).
