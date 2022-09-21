# S6 images

This directory contains assets and tooling for building a variety of Pulp 3 related container images.

For instructions how to run and use this container, see [Pulp in One Container](https://pulpproject.org/pulp-in-one-container/).

# Build instructions

```bash
$ wget https://github.com/just-containers/s6-overlay/releases/download/v3.1.2.1/s6-overlay-x86_64.tar.xz
$ wget https://github.com/just-containers/s6-overlay/releases/download/v3.1.2.1/s6-overlay-noarch.tar.xz
$ wget https://github.com/just-containers/s6-overlay/releases/download/v3.1.2.1/s6-overlay-symlinks-arch.tar.xz
$ wget https://github.com/just-containers/s6-overlay/releases/download/v3.1.2.1/s6-overlay-symlinks-noarch.tar.xz
$ unxz s6-overlay*.tar.xz
$ gzip s6-overlay*.tar
$ <docker build | buildah bud> --file s6_images/pulp_ci_centos/Containerfile --tag pulp/pulp-ci-centos:latest .
$ <docker build | buildah bud> --file s6_images/pulp/Containerfile --tag pulp/pulp:latest .
$ <docker build | buildah bud> --file s6_images/pulp_galaxy_ng/Containerfile --tag pulp/pulp-galaxy-ng:latest .
```

## Specifying versions

By default, containers get built using the latest version of each Pulp component. If you want to
specify a version of a particular component, you can do so with args:

```bash
$ <docker build | buildah bud> --build_arg PULPCORE_VERSION="==3.5.0" --file s6_images/pulp/Containerfile
$ <docker build | buildah bud> --build_arg PULP_FILE_VERSION=">=1.0.0" --file s6_images/pulp/Containerfile
```

# Releasing

We maintain a container tag for every pulpcore y-release (e.g. 3.7, 3.8, ...). When there's a
pulpcore z-release, the existing y-release branch is built and published again.

## Pulpcore Y release

* For a y-release, first create a new release branch (e.g. 3.10) in this pulp-oci-images repo.
* Update PULPCORE_VERSION in pulp/Containerfile on the release branch (see
  [here](https://github.com/pulp/pulp-oci-images/pull/61/files) as an example)
* Kick off a new build from the release branch at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions/workflows/publish_images.yaml)

## Pulpcore Z release

* Go to the y-release branch you're releasing for and make sure the pulp/Containerfile looks good.
* Kick off a new build at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions/workflows/publish_images.yaml)

# Debugging

## Debugging the services

To debug the services and actually see their output, rather than running the usual command to start the container, run a command
like the following (no "--detach", with "-ti", with "/bin/bash" on the end.)
```bash
docker run -ti --name pulp --publish 8080:80 --volume "/$(pwd)/settings:/etc/pulp:Z" --device /dev/fuse pulp/pulp /bin/bash
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
To attempt to manually run a failed service:
```bash
s6-rc change servicename
```
