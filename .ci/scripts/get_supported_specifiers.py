"""
Fetch supported branches for each plugin from their template_config.yml on GitHub
and generate pip version specifiers that constrain installs to those branches.

Can be imported as a module or run as CLI to output pip constraints format.
"""

import argparse
import requests
from yaml import safe_load
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import parse
from urllib.parse import urljoin

GITHUB_RAW = "https://raw.githubusercontent.com/pulp/{repo}/main/template_config.yml"
INDEX = "https://pypi.org"

SKIP = {"pulp-file", "pulp-certguard", "pulpcore"}
SKIP_PREFIX = "pulp-glue"

PACKAGES = [
    "pulp-ansible",
    "pulp-container",
    "pulp-deb",
    "pulp-gem",
    "pulp-hugging-face",
    "pulp-maven",
    "pulp-npm",
    "pulp-ostree",
    "pulp-python",
    "pulp-rpm",
]

PYTHON_VERSIONS = {
    Requirement("pulpcore>=3.22"): "3.11",
}


def pip_to_repo(pip_name):
    return pip_name.replace("-", "_")


def get_supported_branches(repo_name):
    url = GITHUB_RAW.format(repo=repo_name)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        config = safe_load(resp.text)
        branches = [str(b) for b in config.get("supported_release_branches", [])]
        latest = config.get("latest_release_branch")
        if latest:
            branches.append(str(latest))
        return branches
    except Exception:
        return None


def _branch_to_tuple(branch):
    parts = branch.split(".")
    return (int(parts[0]), int(parts[1]))


def build_specifier(branches):
    """Build a pip specifier allowing only versions from the given branches.

    E.g. branches ["0.18", "0.20", "0.21"] -> ">=0.18.0,!=0.19.*,<0.22.0"
    """
    if not branches:
        return None

    tuples = sorted(set(_branch_to_tuple(b) for b in branches))
    supported = set(tuples)
    lo_maj, lo_min = tuples[0]
    hi_maj, hi_min = tuples[-1]

    parts = [f">={lo_maj}.{lo_min}.0"]
    for minor in range(lo_min + 1, hi_min):
        if (lo_maj, minor) not in supported:
            parts.append(f"!={lo_maj}.{minor}.*")
    parts.append(f"<{hi_maj}.{hi_min + 1}.0")
    return ",".join(parts)


def check_installable(pulpcore_version, plugin, specifier):
    """Check if the plugin and its constraints are installable with the given pulpcore version."""
    for core_spread, core_python in PYTHON_VERSIONS.items():
        if pulpcore_version in core_spread.specifier:
            break
    plugin_pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/json"))
    assert plugin_pypi_response.status_code == 200
    plugin_versions = sorted((parse(v) for v in plugin_pypi_response.json()["releases"].keys()), reverse=True)
    for version in plugin_versions:
        if version not in SpecifierSet(specifier):
            continue
        version_pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/{version}/json"))
        assert version_pypi_response.status_code == 200
        version_python_response_json = version_pypi_response.json()
        deps = version_python_response_json["info"]["requires_dist"]
        if deps is None:
            continue
        required_python_version = version_python_response_json["info"]["requires_python"]
        core_dep = next(filter(lambda dep: dep.startswith("pulpcore"), deps))
        if pulpcore_version in Requirement(core_dep).specifier:
            if required_python_version and not SpecifierSet(required_python_version).contains(core_python):
                continue
            return True
    return False


def get_latest_plugin_z_version(plugin, branch):
    """Get the latest z version of the plugin for the given branch."""
    pypi_response = requests.get(urljoin(INDEX, f"pypi/{plugin}/json"))
    assert pypi_response.status_code == 200
    plugin_versions = sorted((parse(v) for v in pypi_response.json()["releases"].keys()), reverse=True)
    target_version = parse(branch)
    for version in plugin_versions:
        if version.major == target_version.major and version.minor == target_version.minor:
            return version
    return None


def get_specifiers(pulpcore_version=None, plugin_names=None):
    """Return dict of {pip_name: specifier_string} for plugins with known support."""
    if pulpcore_version is None:
        pulpcore_version = get_supported_branches("pulpcore")[-1]
    if pulpcore_version.count(".") == 1:
        pulpcore_version = get_latest_plugin_z_version("pulpcore", pulpcore_version)
    if plugin_names is None:
        plugin_names = PACKAGES
    result = {}
    for pip_name in plugin_names:
        if pip_name in SKIP or pip_name.startswith(SKIP_PREFIX):
            continue
        repo = pip_to_repo(pip_name)
        branches = get_supported_branches(repo)
        if branches:
            spec = build_specifier(branches)
            if spec and check_installable(pulpcore_version, pip_name, spec):
                result[pip_name] = spec
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pulpcore-version", required=False)
    parser.add_argument("--plugin-names", required=False)
    opts = parser.parse_args()
    specifiers = get_specifiers(opts.pulpcore_version, opts.plugin_names)
    for name, spec in sorted(specifiers.items()):
        print(f"{name}{spec}")
