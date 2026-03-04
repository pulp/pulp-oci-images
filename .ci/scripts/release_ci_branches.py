import os
import requests
import argparse
import subprocess
import json
from yaml import safe_load
from packaging import version
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from check_up_to_date import check_update
from get_supported_specifiers import get_specifiers


# We use this to check if the version is x,y, like a normal branch.
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github.v3+json",
}

github_api = "https://api.github.com"
core_template_config = "https://raw.githubusercontent.com/pulp/pulpcore/main/template_config.yml"

def main():
    parser = argparse.ArgumentParser(description="Run CI branches")
    parser.add_argument("--optimize", action="store_true", help="Only run the CI for branches that have new versions")
    args = parser.parse_args()
    
    request = requests.get(core_template_config)
    if request.status_code != 200:
        print("Failed to find supported branches")
        exit(1)

    template = safe_load(request.content)
    branches = template.get("supported_release_branches", [])
    plugin_specifiers = get_specifiers()

    for branch in branches:
        if args.optimize:
            cmd = ["oras", "manifest", "fetch-config", "--platform", "linux/amd64", f"ghcr.io/pulp/pulp:{branch}"]
            config = subprocess.check_output(cmd)
            config = json.loads(config)
            plugins = config.get("config", {}).get("Labels", {}).get("org.pulp.plugins", "")
            if plugins:
                versions = {plugin: v for part in plugins.split("\\n") for plugin, _, v in [part.partition("==")]}
                if not check_update(branch, versions, plugin_specifiers=plugin_specifiers, should_exit=False):
                    print(f"No updates needed for {branch}")
                    continue
            else:
                print(f"{branch} didn't have plugins label, running CI")

        print(f"Updating {branch}")
        if isfloat(branch) and version.parse(branch) < version.parse("3.22"):
            workflow_path = "/actions/workflows/publish_images.yaml/dispatches"
        elif isfloat(branch) and version.parse(branch) < version.parse("3.47"):
            workflow_path = "/actions/workflows/pulp_images.yml/dispatches"
        else:
            workflow_path = "/actions/workflows/release.yml/dispatches"
        url = f"{github_api}/repos/pulp/pulp-oci-images{workflow_path}"
        requests.post(url, headers=headers, json={"ref": branch})

if __name__ == "__main__":
    main()
