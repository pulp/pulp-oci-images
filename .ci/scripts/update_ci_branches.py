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

github_api = "https://api.github.com"
core_template_config = "https://raw.githubusercontent.com/pulp/pulpcore/main/template_config.yml"

request = requests.get(core_template_config)
if request.status_code != 200:
    print("Failed to find supported branches")
    exit(1)

template = safe_load(request.content)
branches = template.get("supported_release_branches", [])

for branch in branches:
    print(f"Updating {branch}")
    if isfloat(branch) and version.parse(branch) < version.parse("3.22"):
        workflow_path = "/actions/workflows/publish_images.yaml/dispatches"
    else:
        workflow_path = "/actions/workflows/pulp_images.yml/dispatches"
    url = f"{github_api}/repos/pulp/pulp-oci-images{workflow_path}"
    requests.post(url, headers=headers, json={"ref": branch})
