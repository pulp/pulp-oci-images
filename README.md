# Pulp 3 Containers

This directory contains assets and tooling for building a variety of Pulp 3 related container images.

For instructions how to run and use this container, see [Pulp in One Container](https://pulpproject.org/pulp-in-one-container/).

# Build instructions

```bash
$ wget https://github.com/just-containers/s6-overlay/releases/download/v1.22.1.0/s6-overlay-amd64.tar.gz
$ <docker build | buildah bud> --file pulp_ci_centos/Containerfile --tag pulp/pulp-ci-centos:latest .
$ <docker build | buildah bud> --file pulp/Containerfile --tag pulp/pulp:latest .
$ <docker build | buildah bud> --file pulp_galaxy_ng/Containerfile --tag pulp/pulp-galaxy-ng:latest .
```

## Specifying versions

By default, containers get built using the latest version of each Pulp component. If you want to
specify a version of a particular component, you can do so with args:

```bash
$ <docker build | buildah bud> --build_arg PULPCORE_VERSION="==3.5.0" --file pulp/Containerfile
$ <docker build | buildah bud> --build_arg PULP_FILE_VERSION=">=1.0.0" --file pulp/Containerfile
```

# Releasing

We maintain a container tag for every pulpcore y-release (e.g. 3.7, 3.8, ...). When there's a
pulpcore z-release, the existing y-release branch is built and published again.

## Pulpcore Y release

* For a y-release, first create a new release branch (e.g. 3.10) in this pulp-oci-images repo.
* Update PULPCORE_VERSION in pulp/Containerfile on the release branch (see
  [here](https://github.com/pulp/pulp-oci-images/pull/61/files) as an example)
* Kick off a new build from the release branch at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions?query=workflow%3A%22Build+and+publish+OCI+Images%22)

## Pulpcore Z release

* Go to the y-release branch you're releasing for and make sure the pulp/Containerfile looks good.
* Kick off a new build at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions?query=workflow%3A%22Build+and+publish+OCI+Images%22)
