import os
import re
import requests
from packaging.version import Version
from yaml import safe_load
from git import Repo

repo = Repo(os.getcwd())
heads = repo.git.ls_remote("--heads", "https://github.com/pulp/pulpcore.git").split("\n")
branches = [h.split("/")[-1] for h in heads if re.search(r"^([0-9]+)\.([0-9]+)$", h.split("/")[-1])]
branches.sort(key=lambda ver: Version(ver))

headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github.v3+json",
}
config = requests.get("https://raw.githubusercontent.com/pulp/pulpcore/main/template_config.yml").content
initial_branch = safe_load(config["keep_ci_update_since_branch"])
starting = branches.index(initial_branch)

github_api = "https://api.github.com"
workflow_path = "/actions/workflows/publish_images.yaml/dispatches"
url = f"{github_api}/repos/pulp/pulp-oci-images{workflow_path}"

for branch in branches[starting:]:
    print(f"Updating {branch}")
    requests.post(url, headers=headers, json={"ref": branch})
