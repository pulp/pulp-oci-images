"""
Fetch supported branches for each plugin from their template_config.yml on GitHub
and generate pip version specifiers that constrain installs to those branches.

Can be imported as a module or run as CLI to output pip constraints format.
"""

import requests
from yaml import safe_load

GITHUB_RAW = "https://raw.githubusercontent.com/pulp/{repo}/main/template_config.yml"

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


def get_specifiers(plugin_names=None):
    """Return dict of {pip_name: specifier_string} for plugins with known support."""
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
            if spec:
                result[pip_name] = spec
    return result


if __name__ == "__main__":
    specifiers = get_specifiers()
    for name, spec in sorted(specifiers.items()):
        print(f"{name}{spec}")
