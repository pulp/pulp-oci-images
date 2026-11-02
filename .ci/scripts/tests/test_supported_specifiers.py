import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_up_to_date
import get_supported_specifiers


class SupportedSpecifierTests(unittest.TestCase):
    def select(self, supported, installed="3.37.1", python_version="3.12.15"):
        releases = {"3.38.0": ">=3.13", "3.37.1": ">=3.12", "3.36.4": ">=3.11"}
        responses = {
            "https://pypi.org/pypi/pulpcore/json": {"releases": {"3.123.1": []}},
            "https://pypi.org/pypi/pulp-python/json": {
                "releases": {version: [] for version in releases},
            },
        }
        for version, required_python in releases.items():
            responses[f"https://pypi.org/pypi/pulp-python/{version}/json"] = {
                "info": {
                    "requires_dist": ["pulpcore>=3.105,<3.130"],
                    "requires_python": required_python,
                },
            }

        def get(url):
            return Mock(status_code=200, json=Mock(return_value=responses[url]))

        self.output = io.StringIO()
        with patch.object(get_supported_specifiers.requests, "get", side_effect=get), \
                patch.object(get_supported_specifiers, "get_supported_branches",
                             return_value=supported), \
                contextlib.redirect_stdout(self.output):
            specifiers = get_supported_specifiers.get_specifiers(
                "3.123.1", plugin_names=["pulp-python"], python_version=python_version,
            )
            update = check_up_to_date.check_update(
                "3.123", {"pulpcore": "3.123.1", "pulp-python": installed},
                python_version, plugin_specifiers=specifiers, should_exit=False,
            )
        return specifiers, update

    def test_python_312_supported_branch_emits_constraint_and_selects_upgrade(self):
        specifiers, update = self.select(["3.37"], installed="3.36.4")
        self.assertEqual(specifiers, {"pulp-python": ">=3.37.0,<3.38.0"})
        self.assertTrue(update)
        self.assertIn("pulp-python: 3.36.4 -> 3.37.1", self.output.getvalue())

    def test_python_311_omits_uninstallable_supported_constraint(self):
        specifiers, update = self.select(
            ["3.37"], installed="3.36.4", python_version="3.11.14",
        )
        self.assertEqual(specifiers, {})
        self.assertFalse(update)

    def test_new_supported_branch_selection_requires_downgrade(self):
        specifiers, update = self.select(["3.36"])
        self.assertEqual(specifiers, {"pulp-python": ">=3.36.0,<3.37.0"})
        self.assertTrue(update)
        self.assertIn("pulp-python: 3.37.1 -> 3.36.4", self.output.getvalue())

    def test_rebuilt_image_matching_supported_branch_needs_no_update(self):
        _, update = self.select(["3.36"], installed="3.36.4")
        self.assertFalse(update)

    def test_supported_branch_gap_and_python_compatibility_select_downgrade(self):
        specifiers, update = self.select(["3.36", "3.38"])
        self.assertEqual(specifiers, {"pulp-python": ">=3.36.0,!=3.37.*,<3.39.0"})
        self.assertTrue(update)
        self.assertIn("pulp-python: 3.37.1 -> 3.36.4", self.output.getvalue())

    def test_omitted_uninstallable_constraint_preserves_current_version(self):
        specifiers, update = self.select(["3.38"])
        self.assertEqual(specifiers, {})
        self.assertFalse(update)


if __name__ == "__main__":
    unittest.main()
