# Multi-Process Images

For a quick start guide on how to run and use these containers, see [Pulp in One Container](https://pulpproject.org/pulp-in-one-container/).

For more detailed instructions, see the [PULP OCI Images
docs](https://docs.pulpproject.org/pulp_oci_images/).

## pulp

A single [Pulp](https://github.com/pulp/pulpcore) image that runs Pulp, as well as its third-party
services (nginx, postgresql and redis), in one single Docker/Podman container.

To run all the services, you do not need to specify a container command ("CMD"). The default CMD is:

- **/init** - The [s6 service manager](https://github.com/just-containers/s6-overlay) that runs all the services.

The image can also function the same as the Single-Process image ["pulp-minimal"](#pulp-minimal). Specifically, the image can also be run as as each of the following individual services, specified as the container command ("CMD").

- **pulp-api** - serves the Pulp(v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_. If pulp_ansible, pulp_container or pulp_python are in use, _Content consumers also put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demand on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demand on this service_.

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

  [https://quay.io/repository/pulp/pulp?tab=tags](https://quay.io/repository/pulp/pulp?tab=tags)

## pulp-galaxy-ng

A single [galaxy](https://github.com/ansible/galaxy_ng) image that runs Pulp as well as its third-party
services in one single container: nginx, postgresql and redis.

To run all the services, you do not need to specify a container command ("CMD"). The default CMD is:

- **/init** - The s6 service manager that runs all the services.

The image can also function the same as the Single-Process image ["galaxy-minimal"](#galaxy-minimal). Specifically, the image can also be run as as each of the following individual services, specified as the container command ("CMD").

- **pulp-api** - serves the Pulp(v3) API. The number of instances of this service should be scaled as demand requires. _Content consumers, Administrators and users of all of the APIs put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demand on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demand on this service_.

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `https`: Built nightly, with latest released version of each plugin. Nginx webserver runs with SSL/TLS.

[https://quay.io/repository/pulp/pulp-galaxy-ng?tab=tags](https://quay.io/repository/pulp/pulp-galaxy-ng?tab=tags)

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
