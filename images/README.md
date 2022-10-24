# Single-Process Images

These images are currently used on [pulp operator](https://docs.pulpproject.org/pulp_operator/), but they can be used in docker-compose or podman-compose, you can find an example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose).

## pulp-minimal

A single [pulp](https://github.com/pulp/pulpcore) image that can be run as each of the following services, specified as the container command ("CMD"):

- **pulp-api** - serves the Pulp(v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demands on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demands on this service_.

Currently built with the following plugins:

- [pulp_ansible](https://docs.pulpproject.org/pulp_ansible/)
- [pulp-certguard](https://docs.pulpproject.org/pulp_certguard/)
- [pulp_container](https://docs.pulpproject.org/pulp_container/)
- [pulp_deb](https://docs.pulpproject.org/pulp_deb/)
- [pulp_file](https://docs.pulpproject.org/pulp_file/)
- [pulp_maven](https://docs.pulpproject.org/pulp_maven/)
- [pulp_python](https://docs.pulpproject.org/pulp_python/)
- [pulp_rpm](https://docs.pulpproject.org/pulp_rpm/)

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `nightly`: Built nightly, With master/main branches of each plugin. Also contains several
  additional plugins that are not GA yet.
- `3.y.z`:  Pulpcore 3.y.z version and its compatible plugins.

[https://quay.io/repository/pulp/pulp?tab=tags](https://quay.io/repository/pulp/pulp?tab=tags)

## pulp-web

An Nginx image based on [centos/nginx-116-centos7](https://hub.docker.com/r/centos/nginx-116-centos7),
with pulpcore and plugins specific configuration.

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `nightly`: Built nightly, With master/main branches of each plugin. Also built with several
  additional plugins that are not GA yet.
- `3.y.z`:  Pulpcore 3.y.z version and its compatible plugins.

[https://quay.io/repository/pulp/pulp-web?tab=tags](https://quay.io/repository/pulp/pulp-web?tab=tags)

## galaxy-minimal

An single [galaxy](https://github.com/ansible/galaxy_ng) image that can be run as each of the following services, specified as the container command ("CMD"):

- **pulp-api** - serves the Galaxy (v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demands on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demands on this service_.

### Tags

- `stable`: Built nightly, with latest released version of galaxy and its dependency plugins.
- `nightly`: Built nightly, With master/main branches of each plugin.
- `4.y.z`:  Galaxy 4.y.z version.

[https://quay.io/repository/pulp/galaxy?tab=tags](https://quay.io/repository/pulp/galaxy?tab=tags)

## Galaxy Web

An Nginx image based on [centos/nginx-116-centos7](https://hub.docker.com/r/centos/nginx-116-centos7),
with galaxy specific configuration.

### Tags

- `stable`: Built nightly, with latest released version of galaxy and its dependency plugins.
- `nightly`: Built nightly, with master branch of [galaxy](https://github.com/ansible/galaxy_ng).
- `4.y.z`:  Galaxy 4.y.z version.

[https://quay.io/repository/pulp/galaxy-web?tab=tags](https://quay.io/repository/pulp/galaxy-web?tab=tags)

## Compose

The Podman/Docker Compose file is not production ready yet. You can try it out by running:

```
cd images/compose

podman-compose up -d
```

# S6 Multi-Process images

For a quick start guide on how to run and use these containers, see [Pulp in One Container](https://pulpproject.org/pulp-in-one-container/).

For more detailed instructions, see the [PULP OCI Images
docs](https://docs.pulpproject.org/pulp_oci_images/).

## pulp

A single [pulp](https://github.com/pulp/pulpcore) image that runs Pulp as well as its third-party
services in one single container: nginx, postgresql and redis.

To run all the services, you do not need to specify a container command ("CMD"). The default CMD is:

- **/init** - The s6 service manager that runs all the services.

The image can also function the same as the Single-Process image ["pulp-minimal"](#pulp-minimal). Specifically, the image can also be run as as each of the following individual services, specified as the container command ("CMD").

- **pulp-api** - serves the Pulp(v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demands on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demands on this service_.

Currently built with the following plugins:

- [pulp_ansible](https://docs.pulpproject.org/pulp_ansible/)
- [pulp-certguard](https://docs.pulpproject.org/pulp_certguard/)
- [pulp_container](https://docs.pulpproject.org/pulp_container/)
- [pulp_deb](https://docs.pulpproject.org/pulp_deb/)
- [pulp_file](https://docs.pulpproject.org/pulp_file/)
- [pulp_maven](https://docs.pulpproject.org/pulp_maven/)
- [pulp_python](https://docs.pulpproject.org/pulp_python/)
- [pulp_rpm](https://docs.pulpproject.org/pulp_rpm/)

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `https`: Built nightly, with latest released version of each plugin. Nginx webserver runs with SSL/TLS.
- `nightly`: Built nightly, With master/main branches of each plugin. Also built with several
  additional plugins that are not GA yet.
- `3.y`:  Pulpcore 3.y version and its compatible plugins. Built whenever there is a z-release.
- `3.y-https`:  Pulpcore 3.y version and its compatible plugins. Built whenever there is a z-release. 
  Nginx webserver runs with SSL/TLS.

## pulp-galaxy-ng

A single [galaxy](https://github.com/ansible/galaxy_ng) image that runs Pulp as well as its third-party
services in one single container: nginx, postgresql and redis.

To run all the services, you do not need to specify a container command ("CMD"). The default CMD is:

- **/init** - The s6 service manager that runs all the services.

The image can also function the same as the Single-Process image ["galaxy-minimal"](#galaxy-minimal). Specifically, the image can also be run as as each of the following individual services, specified as the container command ("CMD").

- **pulp-api** - serves the Pulp(v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demands on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demands on this service_.

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `https`: Built nightly, with latest released version of each plugin. Nginx webserver runs with SSL/TLS.

## Build instructions

```bash
$ <docker build | buildah bud> --file images/pulp_ci_centos/Containerfile --tag pulp/pulp-ci-centos:latest .
$ <docker build | buildah bud> --file images/pulp/Containerfile --tag pulp/pulp:latest .
$ <docker build | buildah bud> --file images/pulp_galaxy_ng/Containerfile --tag pulp/pulp-galaxy-ng:latest .
```

### Specifying versions

By default, containers get built using the latest version of each Pulp component. If you want to
specify a version of a particular component, you can do so with args:

```bash
$ <docker build | buildah bud> --build_arg PULPCORE_VERSION="==3.5.0" --file images/pulp/Containerfile
$ <docker build | buildah bud> --build_arg PULP_FILE_VERSION=">=1.0.0" --file images/pulp/Containerfile
```

## Release instructions

We maintain a container tag for every pulpcore y-release (e.g. 3.7, 3.8, ...). When there's a
pulpcore z-release, the existing y-release branch is built and published again.

### Pulpcore Y release

* For a y-release, first create a new release branch (e.g. 3.10) in this pulp-oci-images repo.
* Update PULPCORE_VERSION in pulp/Containerfile on the release branch (see
  [here](https://github.com/pulp/pulp-oci-images/pull/61/files) as an example)
* Kick off a new build from the release branch at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions/workflows/publish_images.yaml)
  (Afterwards, it will auto-build nightly.)

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
