"""Unit tests for ogcapi10.py."""

import json
import unittest

import sedr.ogcapi10 as ogcapi
import sedr.util


class TestOGCAPI(unittest.TestCase):
    __version__ = "testversion"
    sedr.util.args = sedr.util.parse_args(
        ["--url", "https://example.com/"], __version__
    )
    sedr.util.logger = sedr.util.set_up_logging(
        args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
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
