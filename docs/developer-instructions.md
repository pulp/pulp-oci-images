# Developer instructions

## Release instructions (multi-process images)

We maintain a container tag for every pulpcore y-release (e.g. 3.7, 3.8, ...). When there's a
pulpcore z-release, the existing y-release branch is built and published again.

### Pulpcore Y release

* For a y-release, first create a new release branch (e.g. 3.10) in this pulp-oci-images repo.
* Update PULPCORE_VERSION in images/pulp/Containerfile on the release branch (see
  [here](https://github.com/pulp/pulp-oci-images/pull/61/files) as an example)
* Kick off a new build from the release branch at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions/workflows/publish_images.yaml)
  (Afterwards, it will auto-build nightly.)
* Kick off a new build from the release branch at [the publish workflow](https://github.com/pulp/pulp-oci-images/actions/workflows/pulp_images.yml)
  (Afterwards, it will auto-build nightly.)

