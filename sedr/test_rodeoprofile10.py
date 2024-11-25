"""Unit tests for rodeoprofile10.py."""

import unittest
import util
import rodeoprofile10 as profile


class TestRodeoprofile(unittest.TestCase):
    __version__ = "testversion"
    util.args = util.parse_args([], __version__)
    util.logger = util.set_up_logging(
        args=util.args, logfile=util.args.log_file, version=__version__
    )

    def test_requirement7_2(self):
        landing_json_good = {
            "title": "EDR isobaric from Grib",
            "description": "An EDR API for isobaric data from Grib files",
            "links": [
                {
                    "href": "https://edrisobaric.k8s.met.no/",
                    "rel": "self",
                    "type": "application/json",
                    "title": "Landing Page",
                },
                {
                    "href": "https://edrisobaric.k8s.met.no/api",
                    "rel": "service-desc",
                    "type": "application/vnd.oai.openapi+json;version=3.1",
                    "title": "OpenAPI document",
                },
                {
                    "href": "https://edrisobaric.k8s.met.no/docs",
                    "rel": "service-doc",
                    "type": "text/html",
                    "title": "OpenAPI document",
                },
                {
                    "href": "https://edrisobaric.k8s.met.no/conformance",
                    "rel": "conformance",
                    "type": "application/json",
                    "title": "Conformance document",
                },
                {
                    "href": "https://edrisobaric.k8s.met.no/collections",
                    "rel": "data",
                    "type": "application/json",
                    "title": "Collections metadata in JSON",
                },
            ],
            "provider": {
                "name": "Meteorologisk institutt / The Norwegian Meteorological Institute",
                "url": "https://api.met.no/",
            },
            "contact": {
                "email": "weatherapi-adm@met.no",
                "phone": "+47.22963000",
                "address": "Henrik Mohns plass 1",
                "postalCode": "0313",
                "city": "Oslo",
                "country": "Norway",
            },
        }

        ok, _ = profile.requirement7_2(landing_json_good, timeout=10)
        self.assertTrue(ok)

        landing_json_bad = {
            "title": "EDR isobaric from Grib",
            "description": "An EDR API for isobaric data from Grib files",
            "links": [
                {
                    "href": "https://edrisobaric.k8s.met.no/",
                    "rel": "self",
                    "type": "application/json",
                    "title": "Landing Page",
                },
            ],
        }

        ok, _ = profile.requirement7_2(landing_json_bad, timeout=10)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
