#!/usr/bin/env bash
# coding=utf-8
set -euo pipefail

if [[ "${1-}" == "--build" ]] || [[ "${1-}" == "-b" ]]; then
    sed -i "s|images/||g" images/Containerfile.core.base
    # Create a multi-architecture manifest
    buildah manifest create ${MANIFEST_NAME}

    # Build your ppc64le architecture container
    buildah bud \
        --pull=false \
        --tag "${IMAGE}" \
        --manifest ${MANIFEST_NAME} \
        --platform linux/ppc64le \
        --format docker \
        ${BUILD_PATH}

    # Build your arm64 architecture container
    buildah bud \
        --pull=false \
        --tag "${IMAGE}" \
        --manifest ${MANIFEST_NAME} \
        --platform linux/arm64 \
        --format docker \
        ${BUILD_PATH}

    # Build your amd64 architecture container
    buildah bud \
        --pull=false \
        --tag "${IMAGE}" \
        --manifest ${MANIFEST_NAME} \
        --platform linux/amd64 \
        --format docker \
        ${BUILD_PATH}

elif [[ "${1-}" == "--push" ]] || [[ "${1-}" == "-p" ]]; then
    # Push the full manifest, with both CPU Architectures
    buildah manifest push --all \
        ${MANIFEST_NAME} \
        "docker://${IMAGE}"
fi
