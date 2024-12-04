import argparse
import requests
from urllib.parse import urljoin
from packaging.version import parse
from packaging.requirements import Requirement

PACKAGES = [
    "pulp-ansible",
    "pulp-container",
    "pulp-deb",
    "pulp-gem",
    "pulp-maven",
    "pulp-python",
    "pulp-rpm",
    "pulp-ostree"
]

INDEX = "https://pypi.org"

def check_update(branch, current_versions):
    """
    Go through each of the image's main Pulp components and see if there is a new version available.
    """
    new_versions = {}
    # Get the latest Z (or Y) pulpcore release for this branch
    core_pypi_response = requests.get(urljoin(INDEX, "pypi/pulpcore/json"))
    assert core_pypi_response.status_code == 200
    core_version = parse(current_versions["pulpcore"])
    for version, release in core_pypi_response.json()["releases"].items():
        cur_version = parse(version)
        if cur_version > core_version:
            if branch != "latest":
                if cur_version.major != core_version.major or cur_version.minor != core_version.minor:
                    continue
            core_version = cur_version
            new_versions["pulpcore"] = core_version

    # Now check each plugin to see if they need updates
    for plugin in PACKAGES:
        if plugin not in current_versions:
            continue
        plugin_version = parse(current_versions[plugin])
        plugin_pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/json"))
        assert plugin_pypi_response.status_code == 200
        plugin_versions = sorted((parse(v) for v in plugin_pypi_response.json()["releases"].keys()), reverse=True)
        for version in plugin_versions:
            if version <= plugin_version:
                break
            version_pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/{version}/json"))
            assert version_pypi_response.status_code == 200
            deps = version_pypi_response.json()["info"]["requires_dist"]
            core_dep = next(filter(lambda dep: dep.startswith("pulpcore"), deps))
            if core_version in Requirement(core_dep).specifier:
                new_versions[plugin] = version
                break

    if new_versions:
        print("Updates needed for:")
        for plugin, version in new_versions.items():
            print(f"{plugin}: {current_versions[plugin]} -> {version!s}")
        exit(100)

    print("No updates needed :)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("branch")
    parser.add_argument("versions", type=argparse.FileType("r"))
    opts = parser.parse_args()
    versions = {}
    for line in opts.versions:
        plugin, _, version = line.rstrip("\n").partition("==")
        versions[plugin] = version
    check_update(opts.branch, versions)
