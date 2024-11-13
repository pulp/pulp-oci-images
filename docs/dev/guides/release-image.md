# Release an Image

## Release instructions (multi-process images)

We maintain a container tag for every supported pulpcore y-release (e.g. 3.49, 3.63, see 
`supported_release_branches` in [template_config](https://github.com/pulp/pulpcore/blob/main/template_config.yml)).
We also publish a tag for the latest pulpcore Y release nightly. When there's a pulpcore z-release, 
the existing y-release branch is built and published again.

### Pulpcore Y release added to supported branches

* First create a new release branch in this pulp-oci-images repo for the new supported Y release
  (if it does not already exist.)
* Update PULPCORE_VERSION in the following files on the new supported Y release branch
  (see [here](https://github.com/pulp/pulp-oci-images/pull/628) as an example):
  * images/pulp/stable/Containerfile
  * images/pulp-minimal/stable/Containerfile.core
