# Pulp 3 Fedora 31 Container

This directory contains assets and tooling for building Pulp 3 container image based on Fedora 31.

# Build instructions

`<docker build | buildah bud> -f Containerfile -t pulp-fedora31:latest .`
`<docker build | buildah bud> -f Containerfile --target ci-base -t pulp-ci-fedora31:latest .`
