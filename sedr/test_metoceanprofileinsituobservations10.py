"""Unit tests for metoceanprofileinsituobservations10.py."""

import json
import unittest
from unittest.mock import MagicMock

import requests

import sedr.metoceanprofileinsituobservations10 as profileinsitu
import sedr.util


class TestMetOceanprofileInsituObservations(unittest.TestCase):
    __version__ = "testversion"
    sedr.util.args = sedr.util.parse_args(
        ["--url", "https://example.com/"], __version__
    )
    sedr.util.logger = sedr.util.set_up_logging(
        args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
    )

    def test_requirement8_2(self):
        # Bad tests
        with open("testdata/edrisobaric_collection.json", encoding="utf-8") as f:
            collection_json = json.load(f)
        ok, _ = profileinsitu.requirement8_2(collection_json)
        self.assertFalse(ok)

    def test_requirement8_6(self):
        # Bad test
        bad_coveragejson = self.mock_bad_coveragejson_response()
        ok, msg = profileinsitu.requirement8_6(bad_coveragejson)
        self.assertFalse(ok, msg)

        # Good test
        good_coveragejson = self.mock_good_coveragejson_response()
        ok, msg = profileinsitu.requirement8_6(good_coveragejson)
        self.assertTrue(ok, msg)

    def test_requirement8_7(self):
        # Bad test
        bad_coveragejson = self.mock_bad_coveragejson_response()
        ok, msg = profileinsitu.requirement8_7(bad_coveragejson)
        self.assertFalse(ok, msg)

        # Good test
        good_coveragejson = self.mock_good_coveragejson_response()
        ok, msg = profileinsitu.requirement8_7(good_coveragejson)
        self.assertTrue(ok, msg)

    def mock_good_coveragejson_response(self):
        """Mock a good coverage JSON response for testing."""

        good_coveragejson = MagicMock(spec=requests.Response)

        # Set attributes on the mock response object
        good_coveragejson.request = MagicMock()
        good_coveragejson.request.url = (
            "https://api.example.com/collection/example/locations/1"
        )
        good_coveragejson.status_code = 200
        good_coveragejson.headers = {"Content-Type": "application/vnd.cov+json"}
        good_coveragejson.json.return_value = {
            "type": "CoverageCollection",
            "coverages": [
                {
                    "type": "Coverage",
                    "domain": {
                        "type": "Domain",
                        "domainType": "PointSeries",
                        "axes": {
                            "x": {"values": [18.29072]},
                            "y": {"values": [67.49483]},
                            "t": {
                                "values": [
                                    "2025-05-08T08:00:00Z",
                                    "2025-05-08T09:00:00Z",
                                ]
                            },
                        },
                        "referencing": [
                            {
                                "coordinates": ["y", "x"],
                                "system": {
                                    "type": "GeographicCRS",
                                    "id": "OGC:CRS84",
                                },
                            },
                            {
                                "coordinates": ["t"],
                                "system": {
                                    "type": "TemporalRS",
                                    "calendar": "Gregorian",
                                },
                            },
                        ],
                    },
                    "ranges": {
                        "relative_humidity:10.0:point:PT0S": {
                            "type": "NdArray",
                            "dataType": "float",
                            "axisNames": ["t", "y", "x"],
                            "shape": [2, 1, 1],
                            "values": [
                                5600.0,
                                5000.0,
                            ],
                        },
                        "wind_from_direction:10.0:point:PT10M": {
                            "type": "NdArray",
                            "dataType": "float",
                            "axisNames": ["t", "y", "x"],
                            "shape": [2, 1, 1],
                            "values": [
                                147.0,
                                153.0,
                            ],
                        },
                        "wind_speed:10.0:point:PT10M": {
                            "type": "NdArray",
                            "dataType": "float",
                            "axisNames": ["t", "y", "x"],
                            "shape": [2, 1, 1],
                            "values": [
                                4.3,
                                3.2,
                            ],
                        },
                    },
                    "metocean:wigosId": "0-20000-0-02024",
                }
            ],
            "parameters": {
                "relative_humidity:10.0:point:PT0S": {
                    "type": "Parameter",
                    "description": {
                        "en": "Relative humidity at 10.0m, aggregated over PT0S with method 'point'"
                    },
                    "observedProperty": {
                        "id": "https://vocab.nerc.ac.uk/standard_name/relative_humidity",
                        "label": {"en": "Relative humidity"},
                    },
                    "unit": {"label": {"en": "percent"}},
                    "metocean:measurementType": {
                        "method": "point",
                        "duration": "PT0S",
                    },
                    "metocean:standard_name": "relative_humidity",
                    "metocean:level": 10.0,
                },
                "wind_from_direction:10.0:point:PT10M": {
                    "type": "Parameter",
                    "description": {
                        "en": "Wind from direction at 10.0m, aggregated over PT10M with method 'point'"
                    },
                    "observedProperty": {
                        "id": "https://vocab.nerc.ac.uk/standard_name/wind_from_direction",
                        "label": {"en": "Wind from direction"},
                    },
                    "unit": {"label": {"en": "degrees"}},
                    "metocean:measurementType": {
                        "method": "point",
                        "duration": "PT10M",
                    },
                    "metocean:standard_name": "wind_from_direction",
                    "metocean:level": 10.0,
                },
                "wind_speed:10.0:point:PT10M": {
                    "type": "Parameter",
                    "description": {
                        "en": "Wind speed at 10.0m, aggregated over PT10M with method 'point'"
                    },
                    "observedProperty": {
                        "id": "https://vocab.nerc.ac.uk/standard_name/wind_speed",
                        "label": {"en": "Wind speed"},
                    },
                    "unit": {"label": {"en": "m/s"}},
                    "metocean:measurementType": {
                        "method": "point",
                        "duration": "PT10M",
                    },
                    "metocean:standard_name": "wind_speed",
                    "metocean:level": 10.0,
                },
            },
        }

        return good_coveragejson

    def mock_bad_coveragejson_response(self):
        """Mock a bad coverage JSON response for testing."""

        bad_coveragejson = MagicMock(spec=requests.Response)

        # Set attributes on the mock response object
        # The response has these errors:
        #   - referencing system is not same as crs in query.
        #   - no metocean:standard_name in one parameter.
        bad_coveragejson.request = MagicMock()
        bad_coveragejson.request.url = (
            "https://api.example.com/collection/example/locations/1?crs=EPSG:4326"
        )
        bad_coveragejson.status_code = 200
        bad_coveragejson.headers = {"Content-Type": "application/vnd.cov+json"}
        bad_coveragejson.json.return_value = {
            "type": "Coverage",
            "domain": {
                "type": "Domain",
                "domainType": "PointSeries",
                "axes": {
                    "x": {"values": [18.29072]},
                    "y": {"values": [67.49483]},
                    "t": {
                        "values": [
                            "2025-05-08T08:00:00Z",
                            "2025-05-08T09:00:00Z",
                        ]
                    },
                },
                "referencing": [
                    {
                        "coordinates": ["y", "x"],
                        "system": {
                            "type": "GeographicCRS",
                            "id": "http://www.opengis.net/def/crs/EPSG/0/4326",
                        },
                    },
                    {
                        "coordinates": ["t"],
                        "system": {"type": "TemporalRS", "calendar": "Gregorian"},
                    },
                ],
            },
            "parameters": {
                "relative_humidity:10.0:point:PT0S": {
                    "type": "Parameter",
                    "description": {
                        "en": "Relative humidity at 10.0m, aggregated over PT0S with method 'point'"
                    },
                    "observedProperty": {
                        "id": "https://vocab.nerc.ac.uk/standard_name/relative_humidity",
                        "label": {"en": "Relative humidity"},
                    },
                    "unit": {"label": {"en": "percent"}},
                    "metocean:measurementType": {"method": "point", "duration": "PT0S"},
                    "metocean:level": 10.0,
                },
                "wind_from_direction:10.0:point:PT10M": {
                    "type": "Parameter",
                    "description": {
                        "en": "Wind from direction at 10.0m, aggregated over PT10M with method 'point'"
                    },
                    "observedProperty": {
                        "id": "https://vocab.nerc.ac.uk/standard_name/wind_from_direction",
                        "label": {"en": "Wind from direction"},
                    },
                    "unit": {"label": {"en": "degrees"}},
                    "metocean:measurementType": {
                        "method": "point",
                        "duration": "PT10M",
                    },
                    "metocean:standard_name": "wind_from_direction",
                    "metocean:level": 10.0,
                },
                "wind_speed:10.0:point:PT10M": {
                    "type": "Parameter",
                    "description": {
                        "en": "Wind speed at 10.0m, aggregated over PT10M with method 'point'"
                    },
                    "observedProperty": {
                        "id": "https://vocab.nerc.ac.uk/standard_name/wind_speed",
                        "label": {"en": "Wind speed"},
                    },
                    "unit": {"label": {"en": "m/s"}},
                    "metocean:measurementType": {
                        "method": "point",
                        "duration": "PT10M",
                    },
                    "metocean:standard_name": "wind_speed",
                    "metocean:level": 10.0,
                },
            },
            "ranges": {
                "relative_humidity:10.0:point:PT0S": {
                    "type": "NdArray",
                    "dataType": "float",
                    "axisNames": ["t", "y", "x"],
                    "shape": [2, 1, 1],
                    "values": [
                        5600.0,
                        5000.0,
                    ],
                },
                "wind_from_direction:10.0:point:PT10M": {
                    "type": "NdArray",
                    "dataType": "float",
                    "axisNames": ["t", "y", "x"],
                    "shape": [2, 1, 1],
                    "values": [
                        147.0,
                        153.0,
                    ],
                },
                "wind_speed:10.0:point:PT10M": {
                    "type": "NdArray",
                    "dataType": "float",
                    "axisNames": ["t", "y", "x"],
                    "shape": [2, 1, 1],
                    "values": [
                        4.3,
                        3.2,
                    ],
                },
            },
            "metocean:wigosId": "0-20000-0-02024",
        }

        return bad_coveragejson


if __name__ == "__main__":
    unittest.main()
