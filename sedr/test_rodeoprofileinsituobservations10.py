"""Unit tests for rodeoprofileinsituobservations10.py."""

import json
import unittest

import sedr.rodeoprofileinsituobservations10 as profileinsitu
import sedr.util


class TestRodeoprofileInsituObservations(unittest.TestCase):
    __version__ = "testversion"
    sedr.util.args = sedr.util.parse_args(
        ["--url", "https://example.com/"], __version__
    )
    sedr.util.logger = sedr.util.set_up_logging(
        args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
    )

    def test_requirement8_2(self):
        # Bad tests
        with open("testdata/edrisobaric_collection.json", "r", encoding="utf-8") as f:
            collection_json = json.load(f)
        ok, _ = profileinsitu.requirement8_2(collection_json)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
