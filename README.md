# Pulp 3 Fedora 31 Container

This directory contains assets and tooling for building Pulp 3 container image based on Fedora 31.

For instructions how to run and use this container, see [Pulp in One Container](https://pulpproject.org/pulp-in-one-container/).

# Build instructions

```bash
$ wget https://github.com/just-containers/s6-overlay/releases/download/v1.22.1.0/s6-overlay-amd64.tar.gz
$ <docker build | buildah bud> --file pulp_ci/Containerfile --tag pulp/pulp-ci:latest .
$ <docker build | buildah bud> --file pulp_fedora31/Containerfile --tag pulp/pulp-fedora31:latest .
$ <docker build | buildah bud> --file pulp_galaxy_ng/Containerfile --tag pulp/pulp-galaxy-ng:latest .
```

## Specifying versions

By default, containers get built using the latest version of each Pulp component. If you want to
specify a version of a particular component, you can do so with args:

```bash
$ <docker build | buildah bud> --build_arg PULPCORE_VERSION="==3.5.0" --file pulp_fedora31/Containerfile
$ <docker build | buildah bud> --build_arg PULP_FILE_VERSION=">=1.0.0" --file pulp_fedora31/Containerfile
```
