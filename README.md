# Pulp 3 Containers

The [pulp-oci-images](https://github.com/pulp/pulp-oci-images) repository is used to provide container images for running Pulp.
These images represent one of the officially supported Pulp installation methods.
The available images can be divided into two types:

- [Multi-Process Images](multi-process-images) - Images for running a [Pulp](https://github.com/pulp/pulpcore), as well as its [third-party services](#third-party-services),
in a single Docker/Podman container.
- [Single-Process Images](single-process-images) - Images containing a single Pulp service each, which collectively make up a Pulp instance. They can be used via docker-compose or podman-compose, example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose). These images are also used by [pulp operator](https://pulpproject.org/pulp-operator/).

Note that OCI stands for "Open Container Initiative", see [here](https://opencontainers.org/).

## Quickstart

See the [quickstart guide for deploying](https://pulpproject.org/pulp-oci-images/docs/admin/tutorials/quickstart/).


## Available Images

| Name | Description |
| ---- | ----------- |
| pulp | Multi-Process Pulp with several plugins |
| pulp-minimal | Single-Process Pulp with several plugins
| pulp-web | Webserver for pulp-minimal |

## First-Party Services

The first-party services are services written by the Pulp project itself.

They are pulp-api, pulp-content, and pulp-worker.

## Third-Party Services

The third-party services are services written by other open source projects, but
Pulp depends on them as the middle tier in 3-tier application architecture to
run.

The 2 backends are the PostgreSQL database server and the redis caching server.

The 1 frontend is the Nginx webserver, with special config to combine
both pulp-api and pulp-content into one service.

## Get Help

Documentation: [https://pulpproject.org/pulp-oci-images/](https://pulpproject.org/pulp-oci-images/)

Issue Tracker: [https://github.com/pulp/pulp-oci-images/issues](https://github.com/pulp/pulp-oci-images/issues)

Forum: [https://discourse.pulpproject.org/](https://discourse.pulpproject.org/)

Join [**#pulp** on Matrix](https://matrix.to/#/#pulp:matrix.org)

Join [**#pulp-dev** on Matrix](https://matrix.to/#/#pulp-dev:matrix.org) for Developer discussion.
