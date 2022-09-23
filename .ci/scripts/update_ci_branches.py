import os
import requests
from yaml import safe_load

headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github.v3+json",
}
config = requests.get("https://raw.githubusercontent.com/pulp/pulpcore/main/template_config.yml").content
branches = safe_load(config)["ci_update_branches"]

github_api = "https://api.github.com"
workflow_path = "/actions/workflows/publish_images.yaml/dispatches"
url = f"{github_api}/repos/pulp/pulp-oci-images{workflow_path}"

for branch in branches:
    print(f"Updating {branch}")
    requests.post(url, headers=headers, json={"ref": branch})
