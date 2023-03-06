import os
import requests
from yaml import safe_load
from packaging import version

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
config = requests.get("https://raw.githubusercontent.com/pulp/pulpcore/main/template_config.yml").content
branches = safe_load(config)["ci_update_branches"]

github_api = "https://api.github.com"

for branch in branches:
    print(f"Updating {branch}")
    if isfloat(branch) and version.parse(branch) < version.parse("3.23") :
        workflow_path = "/actions/workflows/publish_images.yaml/dispatches"
    else:
        workflow_path = "/actions/workflows/pulp_images.yml/dispatches"
    url = f"{github_api}/repos/pulp/pulp-oci-images{workflow_path}"
    requests.post(url, headers=headers, json={"ref": branch})
