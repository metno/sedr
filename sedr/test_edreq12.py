"""Unit tests for edreq12.py."""

import unittest
import json
import sedr.util
import sedr.edreq12 as edreq


class TestEDR(unittest.TestCase):
    __version__ = "testversion"
    sedr.util.args = sedr.util.parse_args(["--url", "https://example.com/"], __version__)
    sedr.util.logger = sedr.util.set_up_logging(
        args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
    )

    def test_requrementA5_2(self):
        """Test extent spatial bbox"""
        # Good tests
        for test_file in [
            "edrisobaric_collection.json",
            "edrisobaric_collection_bbox2.json",
        ]:
            jsondata = {}
            with open(f"testdata/{test_file}", "r", encoding="utf-8") as f:
                jsondata = json.load(f)
            ok, _ = edreq.requrementA5_2(jsondata)
            self.assertTrue(ok)

        # Bad tests
        jsondata = {}
        with open(
            "testdata/edrisobaric_collection_bad_bbox.json", "r", encoding="utf-8"
        ) as f:
            jsondata = json.load(f)
        ok, _ = edreq.requrementA5_2(jsondata)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
