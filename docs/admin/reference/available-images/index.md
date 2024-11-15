# Available Images

## Overview

The available images can be divided into two types:

- [Multi-Process Images](multi-process-images) - Images for running a [Pulp](https://github.com/pulp/pulpcore) or [Ansible Galaxy](https://github.com/ansible/galaxy_ng), as well as its [third-party services](#third-party-services),
in a single Docker/Podman container.
- [Single-Process Images](single-process-images) - Images containing a single Pulp service each, which collectively make up a Pulp instance. They can be used via docker-compose or podman-compose, example [here](https://github.com/pulp/pulp-oci-images/tree/latest/images/compose). These images are also used by [pulp operator](site:pulp-operator).

| Name | Description |
| ---- | ----------- |
| pulp | Multi-Process Pulp with several plugins |
| pulp-minimal | Single-Process Pulp with several plugins
| pulp-web | Webserver for pulp-minimal |
| galaxy | Multi-Process Ansible Galaxy |
| galaxy-minimal | Single-Process Ansible Galaxy |
| galaxy-web | Webserver for galaxy-minimal |

!!! note "Note on Galaxy images"
    
    We are no longer building any newer image versions of galaxy-ng>=4.10. We will still continue
    to build new Z-updates for existing tags, but going forward the `stable` and `latest` tags are
    now discontinued. 

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

