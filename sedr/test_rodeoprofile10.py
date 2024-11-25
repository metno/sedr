"""Unit tests for rodeoprofile10.py."""

import unittest
import json
import util
import rodeoprofile10 as profile


class TestRodeoprofile(unittest.TestCase):
    __version__ = "testversion"
    util.args = util.parse_args([], __version__)
    util.logger = util.set_up_logging(
        args=util.args, logfile=util.args.log_file, version=__version__
    )

    def test_requirement7_2(self):
        # Good tests
        landing_json = {}
        with open("testdata/edrisobaric_landing.json", "r", encoding="utf-8") as f:
            landing_json = json.load(f)
        ok, _ = profile.requirement7_2(landing_json, timeout=10)
        self.assertTrue(ok)

        # Bad tests
        with open(
            "testdata/edrisobaric_landing-bad-desc.json", "r", encoding="utf-8"
        ) as f:
            landing_json = json.load(f)
        ok, _ = profile.requirement7_2(landing_json, timeout=10)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
