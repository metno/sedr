"""Unit tests for util.py."""

import unittest
import json
import util


class TestUtil(unittest.TestCase):
    def test_parse_landing_json(self):
        """Test parsing a generic landing page in json."""
        with open("testdata/landingpage.json", "r", encoding="utf-8") as f:
            landingpage_json = json.loads(f.read())
        landing, _ = util.parse_landing_json(landingpage_json)
        self.assertTrue(landing)

    # def test_parse_bad_landing(self):
    #     """Test parsing a bad landing page (in json)."""
    #     with open("testdata/landingpage_bad_service-desc.json", "r", encoding="utf-8") as f:
    #         landingpage_json = json.loads(f.read())
    #     landing, _ = util.parse_landing_json(landingpage_json)
    #     self.assertFalse(landing)
