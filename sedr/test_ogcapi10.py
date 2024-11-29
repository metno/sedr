"""Unit tests for ogcapi10.py."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import unittest
import json
import util
import ogcapi10 as ogcapi


class TestOGCAPI(unittest.TestCase):
    __version__ = "testversion"
    util.args = util.parse_args(["--url", "https://example.com/"], __version__)
    util.logger = util.set_up_logging(
        args=util.args, logfile=util.args.log_file, version=__version__
    )

    def test_requirement9_1(self):
        # Good tests
        jsondata = {}
        with open("testdata/edrisobaric_landing.json", "r", encoding="utf-8") as f:
            jsondata = json.load(f)
        ok, _ = ogcapi.requirement9_1(jsondata)
        self.assertTrue(ok)

        # Bad tests
        jsondata = {}
        with open(
            "testdata/edrisobaric_landing-bad-desc.json", "r", encoding="utf-8"
        ) as f:
            jsondata = json.load(f)
        ok, _ = ogcapi.requirement9_1(jsondata)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
