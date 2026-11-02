import contextlib
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_up_to_date

with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
    import release_ci_branches


class CheckUpdateTests(unittest.TestCase):
    def check_update(self, installed="3.37.1", python_version="3.12.15", releases=None,
                     branch="latest", plugin_specifiers=None, core_releases=None,
                     should_exit=False):
        releases = releases if releases is not None else {
            "3.37.1": ">=3.12", "3.36.4": ">=3.11"
        }
        responses = {
            "https://pypi.org/pypi/pulpcore/json": {
                "releases": {v: [] for v in (core_releases or ["3.123.1"])}
            },
            "https://pypi.org/pypi/pulp-python/json": {
                "releases": {v: [] for v in releases}
            },
        }
        for version, required_python in releases.items():
            responses[f"https://pypi.org/pypi/pulp-python/{version}/json"] = {
                "info": {
                    "requires_dist": ["pulpcore>=3.105,<3.130"],
                    "requires_python": required_python,
                }
            }

        def get(url):
            return Mock(status_code=200, json=Mock(return_value=responses[url]))

        self.output = io.StringIO()
        with patch.object(check_up_to_date.requests, "get", side_effect=get), \
                contextlib.redirect_stdout(self.output):
            return check_up_to_date.check_update(
                branch, {"pulpcore": "3.123.1", "pulp-python": installed},
                python_version, plugin_specifiers=plugin_specifiers, should_exit=should_exit,
            )

    def test_current_python_312_plugin_does_not_trigger_rebuild(self):
        self.assertFalse(self.check_update())

    def test_new_python_312_plugin_triggers_rebuild(self):
        self.assertTrue(self.check_update(installed="3.36.4"))
        self.assertIn("pulp-python: 3.36.4 -> 3.37.1", self.output.getvalue())

    def test_new_plugin_incompatible_with_image_python_is_skipped(self):
        self.assertFalse(self.check_update(installed="3.36.4", python_version="3.11.14"))

    def test_selection_uses_image_python_when_installed_version_is_incompatible(self):
        self.assertTrue(self.check_update(python_version="3.11.14"))
        self.assertIn("pulp-python: 3.37.1 -> 3.36.4", self.output.getvalue())

    def test_changed_supported_branches_trigger_downgrade(self):
        self.assertTrue(self.check_update(
            branch="3.123", plugin_specifiers={"pulp-python": "<3.37"},
        ))
        self.assertIn("pulp-python: 3.37.1 -> 3.36.4", self.output.getvalue())

    def test_constrained_downgrade_requires_compatible_python(self):
        self.assertFalse(self.check_update(
            branch="3.123", plugin_specifiers={"pulp-python": "<3.37"},
            releases={"3.37.1": ">=3.12", "3.36.4": ">=3.13"},
        ))

    def test_changed_constraints_without_installable_version_do_not_select_downgrade(self):
        self.assertFalse(self.check_update(
            branch="3.123", plugin_specifiers={"pulp-python": "<3.36"},
        ))

    def test_supported_branch_with_current_python_312_plugin_does_not_rebuild(self):
        self.assertFalse(self.check_update(
            branch="3.123", plugin_specifiers={"pulp-python": ">=3.36,<3.38"},
        ))

    def test_latest_branch_ignores_constraints_requiring_downgrade(self):
        self.assertFalse(self.check_update(
            plugin_specifiers={"pulp-python": "<3.37"},
        ))

    def test_newer_constrained_plugin_is_skipped(self):
        self.assertFalse(self.check_update(
            installed="3.36.4", branch="3.123",
            plugin_specifiers={"pulp-python": "<3.37"},
        ))

    def test_latest_branch_ignores_plugin_constraints(self):
        self.assertTrue(self.check_update(
            installed="3.36.4", plugin_specifiers={"pulp-python": "<3.37"},
        ))

    def test_newer_compatible_version_is_selected(self):
        self.assertTrue(self.check_update(
            installed="3.36.3", python_version="3.11.14",
        ))
        self.assertIn("pulp-python: 3.36.3 -> 3.36.4", self.output.getvalue())

    def test_stable_branch_ignores_other_pulpcore_branches(self):
        self.assertFalse(self.check_update(branch="3.123", core_releases=["3.124.0"]))

    def test_pulpcore_patch_triggers_rebuild(self):
        self.assertTrue(self.check_update(branch="3.123", core_releases=["3.123.2"]))

    def test_cli_update_exit_code(self):
        with self.assertRaises(SystemExit) as result:
            self.check_update(installed="3.36.4", should_exit=True)
        self.assertEqual(result.exception.code, 100)

    def test_cli_downgrade_exit_code(self):
        with self.assertRaises(SystemExit) as result:
            self.check_update(
                branch="3.123", plugin_specifiers={"pulp-python": "<3.37"},
                should_exit=True,
            )
        self.assertEqual(result.exception.code, 100)


class ReleaseBranchesTests(unittest.TestCase):
    def run_dispatcher(self, python_version, update_needed=False):
        labels = {"org.pulp.plugins": "pulpcore==3.123.1\\npulp-python==3.37.1"}
        if python_version is not None:
            labels["org.pulp.python-version"] = python_version
        config = {"config": {"Labels": labels}}
        with patch.object(sys, "argv", ["release_ci_branches.py", "--optimize"]), \
                patch.object(release_ci_branches.requests, "get") as get, \
                patch.object(release_ci_branches.requests, "post") as post, \
                patch.object(release_ci_branches.subprocess, "check_output",
                             return_value=release_ci_branches.json.dumps(config)), \
                patch.object(release_ci_branches, "get_specifiers", return_value={}) as specifiers, \
                patch.object(release_ci_branches, "check_update",
                             return_value=update_needed) as check, \
                contextlib.redirect_stdout(io.StringIO()):
            get.return_value.status_code = 200
            get.return_value.content = b"supported_release_branches: ['3.123']"
            release_ci_branches.main()
        if python_version:
            specifiers.assert_called_once_with("3.123", python_version=python_version)
        else:
            specifiers.assert_not_called()
        return check, post

    def test_passes_image_python_and_skips_unchanged_branch(self):
        check, post = self.run_dispatcher("3.12.15")
        check.assert_called_once_with(
            "3.123", {"pulpcore": "3.123.1", "pulp-python": "3.37.1"}, "3.12.15",
            plugin_specifiers={}, should_exit=False,
        )
        post.assert_not_called()

    def test_dispatches_branch_with_updates(self):
        _, post = self.run_dispatcher("3.12.15", update_needed=True)
        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs["json"], {"ref": "3.123"})

    def test_missing_python_label_dispatches_without_guessing(self):
        check, post = self.run_dispatcher(None)
        check.assert_not_called()
        post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
