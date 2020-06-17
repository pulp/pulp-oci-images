# Pulp 3 Fedora 31 Container

This directory contains assets and tooling for building Pulp 3 container image based on Fedora 31.

# Build instructions

`<docker build | buildah bud> -f Containerfile -t pulp-fedora31:latest .`
`<docker build | buildah bud> -f Containerfile --target ci-base -t pulp-ci:latest .`

# Running instructions

```bash
$ mkdir settings pulp_storage pgsql containers
$ echo "CONTENT_ORIGIN='http://$(hostname):8080'
ANSIBLE_API_HOSTNAME='http://$(hostname):8080'
ANSIBLE_CONTENT_HOSTNAME='http://$(hostname):8080/pulp/content'
TOKEN_AUTH_DISABLED=True" >> settings/settings.py
```

### With SELinux

```bash
$ podman run --detach \
             --publish 8080:80 \
             --name pulp \
             --volume ./settings:/etc/pulp:Z \
             --volume ./pulp_storage:/var/lib/pulp:Z \
             --volume ./pgsql:/var/lib/pgsql:Z \
             --volume ./containers:/var/lib/containers:Z \
             --device /dev/fuse \
             pulp/pulp-fedora31
```

### Without SELinux

```bash
$ podman run --detach \
             --publish 8080:80 \
             --name pulp \
             --volume ./settings:/etc/pulp \
             --volume ./pulp_storage:/var/lib/pulp \
             --volume ./pgsql:/var/lib/pgsql \
             --volume ./containers:/var/lib/containers \
             --device /dev/fuse \
             pulp/pulp-fedora31
```

### Reseting the ‘admin’ user’s password

```bash
$ podman exec -it pulp bash -c 'pulpcore-manager reset-admin-password'
Please enter new password for user "admin":
Please enter new password for user "admin" again:
Successfully set password for "admin" user.
```
