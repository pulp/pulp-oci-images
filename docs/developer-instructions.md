# Developer instructions

## Release instructions (multi-process images)

We maintain a container tag for every pulpcore y-release (e.g. 3.7, 3.8, ...). When there's a
pulpcore z-release, the existing y-release branch is built and published again.

### Pulpcore Y release

* First create a new release branch in this pulp-oci-images repo for the prior Y release
  (if it does not already exist.) So if you are releasing 3.23, create the 3.22 branch.
* Update PULPCORE_VERSION in images/pulp/stable/Containerfile on the release branch (see
  [here](https://github.com/pulp/pulp-oci-images/pull/61/files) as an example)
* Update `branches` in `.ci/scripts/update_ci_branches.py` to include the prior Y release.
* Kick off a new build from the release branch at [the workflow](https://github.com/pulp/pulp-oci-images/actions/workflows/pulp_images.yml)
  (Afterwards, it will auto-build nightly.)

