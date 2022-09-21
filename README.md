# Pulp 3 Containers

This directory contains assets and tooling for building a variety of Pulp 3 related container images.

For instructions how to run and use:

- [Images](https://docs.pulpproject.org/pulp_oci_images/images/) to install Pulp 3's [first-party services](#first-party-services)
- [S6 images](https://docs.pulpproject.org/pulp_oci_images/s6_images/) to install Pulp 3's first & [third-party services](#third-party-services)

### First-Party Services

The first-party services are services written by the Pulp project itself.

### Third-Party Services

The third-party services are services written by other open source projects, but
Pulp depends on them as the middle tier in 3-tier application architecture to
run.

The 2 backends are the PostgreSQL database server and the redis server.

The 1 frontend is the Nginx or Apache webserver, with special config to combine
multiple Pulp services into one.

## Get Help

Documentation: [https://docs.pulpproject.org/pulp_oci_images/](https://docs.pulpproject.org/pulp_oci_images/)

Issue Tracker: [https://github.com/pulp/pulp-oci-images/issues](https://github.com/pulp/pulp-oci-images/issues)

Forum: [https://discourse.pulpproject.org/](https://discourse.pulpproject.org/)

Join [**#pulp** on Matrix](https://matrix.to/#/#pulp:matrix.org)

Join [**#pulp-dev** on Matrix](https://matrix.to/#/#pulp-dev:matrix.org) for Developer discussion.
