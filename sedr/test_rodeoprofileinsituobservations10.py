"""Unit tests for rodeoprofileinsituobservations10.py."""

__author__ = "MET Norway"
__license__ = "GPL-2.0"

import unittest
import json
import rodeoprofileinsituobservations10 as profileinsitu
import util


class TestRodeoprofileInsituObservations(unittest.TestCase):
    __version__ = "testversion"
    util.args = util.parse_args(["--url", "https://example.com/"], __version__)
    util.logger = util.set_up_logging(
        args=util.args, logfile=util.args.log_file, version=__version__
    )

    def test_requirement8_2(self):
        # Bad tests
        with open("testdata/edrisobaric_collection.json", "r", encoding="utf-8") as f:
            collection_json = json.load(f)
        ok, _ = profileinsitu.requirement8_2(collection_json)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
