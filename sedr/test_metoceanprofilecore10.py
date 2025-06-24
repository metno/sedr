"""Unit tests for metoceanprofile10.py."""

import json
import unittest

import requests

import sedr.metoceanprofilecore10 as profilecore
import sedr.util


class TestMetoceanprofile(unittest.TestCase):
    __version__ = "testversion"
    sedr.util.args = sedr.util.parse_args(
        ["--url", "https://example.com/"], __version__
    )
    sedr.util.logger = sedr.util.set_up_logging(
        args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
    )

    def test_requirement7_2(self):
        # Good tests
        landing_json = {}
        with open("testdata/edrisobaric_landing.json", encoding="utf-8") as f:
            landing_json = json.load(f)
        ok, _ = profilecore.requirement7_2(landing_json, timeout=10)
        self.assertTrue(ok)

        # Bad tests
        with open("testdata/edrisobaric_landing-bad-desc.json", encoding="utf-8") as f:
            landing_json = json.load(f)
        ok, _ = profilecore.requirement7_2(landing_json, timeout=10)
        self.assertFalse(ok)

    def test_requirement7_12(self):
        def mock_response(
            content, status_code=200, content_type="application/geo+json"
        ):
            response = requests.Response()
            response._content = content.encode("utf-8")  # pylint: disable=protected-access
            response.status_code = status_code
            response.headers["Content-Type"] = content_type
            return response

        # Example usage of the mock_response function
        # How is this wrong: id not string, no name in properties.
        geojson_erroneous_content = """
        {
            "type": "FeatureCollection",
            "features": [
            {
                "type": "Feature",
                "id": 1,
                "properties": {
                    "title": "Test Feature"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]
                }
            }
            ]
        }
        """
        # Example usage of the mock_response function
        geojson_correct_content = """
        {
            "type": "FeatureCollection",
            "features": [
            {
                "type": "Feature",
                "id": "identifier1",
                "properties": {
                    "name": "Test Feature"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]
                }
            }
            ]
        }
        """

        erroneous_response = mock_response(geojson_erroneous_content)
        ok, msg = profilecore.requirement7_12(erroneous_response)
        self.assertFalse(ok, f"Expected errors in response; Got {msg}")

        erroneous_response = mock_response(geojson_correct_content)
        ok, msg = profilecore.requirement7_12(erroneous_response)
        self.assertTrue(ok, f"Expected correct response; Got {msg}")


if __name__ == "__main__":
    unittest.main()
