# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template and copied over to this repository :)
#
# For more info visit https://github.com/pulp/plugin_template

import re
import sys
from pathlib import Path
import subprocess
import os
import warnings
from github import Github

CHANGELOG_EXTS = [".feature", ".bugfix", ".doc", ".removal", ".misc", ".deprecation"]
KEYWORDS = ["fixes", "closes"]

sha = sys.argv[1]
message = subprocess.check_output(["git", "log", "--format=%B", "-n 1", sha]).decode("utf-8")

g = Github(os.environ.get("GITHUB_TOKEN"))
repo = g.get_repo("pulp/pulp-oci-images")


def __check_status(issue):
    gi = repo.get_issue(int(issue))
    if gi.pull_request:
        sys.exit(f"Error: issue #{issue} is a pull request.")
    if gi.closed_at and "cherry picked from commit" not in message:
        warnings.warn(
            "When backporting, use the -x flag to append a line that says "
            "'(cherry picked from commit ...)' to the original commit message."
        )
        sys.exit(f"Error: issue #{issue} is closed.")


def __check_changelog(issue):
    matches = list(Path("CHANGES").rglob(f"{issue}.*"))

    if len(matches) < 1:
        sys.exit(f"Could not find changelog entry in CHANGES/ for {issue}.")
    for match in matches:
        if match.suffix not in CHANGELOG_EXTS:
            sys.exit(f"Invalid extension for changelog entry '{match}'.")
        if match.suffix == ".feature" and "cherry picked from commit" in message:
            sys.exit(f"Can not backport '{match}' as it is a feature.")


print("Checking commit message for {sha}.".format(sha=sha[0:7]))

# validate the issue attached to the commit
regex = r"(?:{keywords})[\s:]+#(\d+)".format(keywords=("|").join(KEYWORDS))
pattern = re.compile(regex, re.IGNORECASE)

issues = pattern.findall(message)

if issues:
    for issue in pattern.findall(message):
        __check_status(issue)
        __check_changelog(issue)

print("Commit message for {sha} passed.".format(sha=sha[0:7]))
