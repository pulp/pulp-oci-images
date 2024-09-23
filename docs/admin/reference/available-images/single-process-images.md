# Single-Process Images

These images are currently used on [pulp operator](site:pulp-operator), but they can be used in docker-compose or podman-compose. You can find a compose example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose).

## pulp-minimal

A single [Pulp](https://github.com/pulp/pulpcore) image that can be run as each of the following services, specified as the container command ("CMD"):

- **pulp-api** - serves the Pulp(v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_. If pulp_python or pulp_container are in use, _Content consumers also put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demand on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demand on this service_.

For complete documentation on how to use this image,
see the compose example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose).
It is the reference on how this image can be used to create the 3 services/containers.

pulp-minimal is currently built with the following plugins:

- [pulp_ansible](site:pulp_ansible)
- [pulp-certguard](site:pulp_certguard)
- [pulp_container](site:pulp_container)
- [pulp_deb](site:pulp_deb)
- [pulp_file](site:pulp_file)
- [pulp_maven](site:pulp_maven)
- [pulp_python](site:pulp_python)
- [pulp_rpm](site:pulp_rpm)
- [pulp_ostree](site:pulp_ostree)

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `nightly`: Built nightly, With master/main branches of each plugin. Also contains several
  additional plugins that are not GA yet.
- `3.y.z`:  Pulpcore 3.y.z version and its compatible plugins.

[https://quay.io/repository/pulp/pulp-minimal?tab=tags](https://quay.io/repository/pulp/pulp-minimal?tab=tags)

## pulp-web

An Nginx image based on [centos/nginx-116-centos7](https://hub.docker.com/r/centos/nginx-116-centos7),
with configuration specific to the plugins found in [pulp-minimal](#pulp-minimal).

No command ("CMD") needs to be specified, the images's built-in command is sufficient.

For complete documentation on how to use this image,
see the compose example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose).
It is the reference on how this image can be used.

### Tags

- `stable`: Built nightly, with latest released version of each plugin. Also called `latest`.
- `nightly`: Built nightly, With master/main branches of each plugin. Also built with several
  additional plugins that are not GA yet.
- `3.y.z`:  Pulpcore 3.y.z version and its compatible plugins.

[https://quay.io/repository/pulp/pulp-web?tab=tags](https://quay.io/repository/pulp/pulp-web?tab=tags)

## galaxy-minimal

An single [galaxy](https://github.com/ansible/galaxy_ng) image that can be run as each of the following services, specified as the container command ("CMD"):

- **pulp-api** - serves the Galaxy (v3) API. The number of instances of this service should be scaled as demand requires.  _Administrators and users of all of the APIs put demand on this service_. _Content consumers also put demand on this service_.

- **pulp-content** - serves content to clients. pulpcore-api redirects clients to pulpcore-content to download content. When content is being mirrored from a remote source, this service can download that content and stream it to the client the first time the content is requested. The number of instances of this service should be scaled as demand requires. _Content consumers put demand on this service_.

- **pulp-worker** - performs syncing, importing of content, and other asynchronous operations that require resource locking. The number of instances of this service should be scaled as demand requires. _Administrators and content importers put demand on this service_.

For complete documentation on how to use this image,
see the compose example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose).
It is the reference on how this image can be used to create the 3 services/containers.
(You will have to replace references to "pulp-minimal" and "pulp-web" with "galaxy-minimal"
and "galaxy-web" respectively.)

### Tags

- `stable`: Built nightly, with latest released version of galaxy.
- `nightly`: Built nightly, With master/main branch galaxy.
- `4.y.z`:  Galaxy 4.y.z version.

[https://quay.io/repository/pulp/galaxy-minimal?tab=tags](https://quay.io/repository/pulp/galaxy-minimal?tab=tags)

## galaxy-web

An Nginx image based on [centos/nginx-116-centos7](https://hub.docker.com/r/centos/nginx-116-centos7),
with configuration specific to the plugins found in [galaxy-minimal](#galaxy-minimal).

For complete documentation on how to use this image,
see the compose example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose).
It is the reference on how this image can be used.
(You will have to replace references to "pulp-minimal" and "pulp-web" with "galaxy-minimal"
and "galaxy-web" respectively.)

### Tags

- `stable`: Built nightly, with latest released version of galaxy.
- `nightly`: Built nightly, With master/main branch galaxy.
- `4.y.z`:  Galaxy 4.y.z version.

[https://quay.io/repository/pulp/galaxy-web?tab=tags](https://quay.io/repository/pulp/galaxy-web?tab=tags)
