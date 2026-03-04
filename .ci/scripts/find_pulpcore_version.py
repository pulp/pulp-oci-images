import argparse
import requests
from packaging.version import parse
import tomllib


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--branch",
        required=True,
        help="The branch we are trying to find the latest pulpcore z version on",
    )
    opts = parser.parse_args()
    version = ""
    if opts.branch == "main":
        # Used for nightly image, find the pulpcore version from @main
        r = requests.get("https://raw.githubusercontent.com/pulp/pulpcore/refs/heads/main/pyproject.toml")
        if r.status_code == 200:
            config = tomllib.loads(r.text)
            if "project" in config:
                version = config["project"]["version"]
            else:
                print("Failed to find current version on main")
                exit(1)
        else:
            print("Failed to download current version on main")
            exit(1)
    else:
        r = requests.get("https://pypi.org/pypi/pulpcore/json")
        if r.status_code == 200:
            metadata = r.json()
            if opts.branch == "latest":
                version = metadata["info"]["version"]
            else:
                releases = metadata["releases"]
                branch_version = parse(opts.branch)
                max_z_version = branch_version
                for version_str in releases.keys():
                    version = parse(version_str)
                    if version.major == branch_version.major and version.minor == branch_version.minor:
                        if version > max_z_version:
                            max_z_version = version
                version = f"{max_z_version.major}.{max_z_version.minor}.{max_z_version.micro}"
        else:
            print("Failed to download pulpcore metadata")
            exit(1)
    print(version)
