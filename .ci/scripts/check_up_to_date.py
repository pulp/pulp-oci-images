import argparse
import requests
from urllib.parse import urljoin
from packaging.version import parse
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

PACKAGES = [
    "pulp-ansible",
    "pulp-container",
    "pulp-deb",
    "pulp-gem",
    "pulp-hugging-face",
    "pulp-maven",
    "pulp-npm",
    "pulp-python",
    "pulp-rpm",
]

INDEX = "https://pypi.org"

PYTHON_VERSIONS = {
    Requirement("pulpcore>=3.22,<3.85"): "3.9",
    Requirement("pulpcore>=3.85"): "3.11"
}

def check_update(branch, current_versions, plugin_specifiers=None, should_exit=True):
    """
    Go through each of the image's main Pulp components and see if there is a new version available.
    """
    new_versions = {}
    plugin_specifiers = plugin_specifiers or {}
    if plugin_specifiers and branch == "latest":
        plugin_specifiers = {}  # latest branch should always check plugins' latest versions

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
    for core_spread, core_python in PYTHON_VERSIONS.items():
        if core_version in core_spread.specifier:
            break

    # Now check each plugin to see if they need updates
    for plugin in PACKAGES:
        if plugin not in current_versions:
            continue
        plugin_version = parse(current_versions[plugin])
        plugin_pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/json"))
        assert plugin_pypi_response.status_code == 200
        plugin_versions = sorted((parse(v) for v in plugin_pypi_response.json()["releases"].keys()), reverse=True)
        for version in plugin_versions:
            if plugin in plugin_specifiers and version not in SpecifierSet(plugin_specifiers[plugin]):
                continue
            version_pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/{version}/json"))
            assert version_pypi_response.status_code == 200
            version_python_response_json = version_pypi_response.json()
            deps = version_python_response_json["info"]["requires_dist"]
            if deps is None:
                print(f"No requires_dist for {plugin} {version}")
                continue
            required_python_version = version_python_response_json["info"]["requires_python"]
            core_dep = next(filter(lambda dep: dep.startswith("pulpcore"), deps))
            if core_version in Requirement(core_dep).specifier:
                if required_python_version and not SpecifierSet(required_python_version).contains(core_python):
                    continue
                new_versions[plugin] = version
                break
        if plugin in new_versions and version == plugin_version:
            del new_versions[plugin]

    if new_versions:
        print("Updates needed for:")
        for plugin, version in new_versions.items():
            print(f"{plugin}: {current_versions[plugin]} -> {version!s}")
        if should_exit:
            exit(100)
        else:
            return True

    print("No updates needed :)")
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("branch")
    parser.add_argument("versions", help="pip freeze like file for current installed versions")
    parser.add_argument("--plugin-specifiers", help="pip constraints file for plugin supported versions", required=False)
    opts = parser.parse_args()
    versions = {}
    plugin_specifiers = {}
    with open(opts.versions) as f:
        lines = f.readlines()
        for line in lines:
            plugin, _, version = line.rstrip("\n").partition("==")
            versions[plugin] = version
    if opts.plugin_specifiers:
        with open(opts.plugin_specifiers) as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                plugin, ge, specifier = line.rstrip("\n").partition(">=")
                plugin_specifiers[plugin] = ge + specifier
    check_update(opts.branch, versions, plugin_specifiers=plugin_specifiers)
