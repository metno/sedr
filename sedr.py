import requests
import schemathesis
from hypothesis import settings
import pytest
import json
import sys
import argparse
import logging
import shapely
from shapely.wkt import loads as wkt_loads
from urllib.parse import urlsplit

sedr_version = "v0.7.0"
edr_version = "1.1"

# Globals
extents = {}
collection_ids = {}


def parse_args() -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="schemathesis-edr")
    parser.add_argument(
        "--openapi",
        type=str,
        help="URL to openapi spec for API",
        default="https://edrisobaric.k8s.met.no/api",
    )
    parser.add_argument(
        "--url", type=str, help="URL to API", default="https://edrisobaric.k8s.met.no"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Amount of examples to generate, per test",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Log output",
    )
    parser.add_argument(
        "--openapi-version",
        choices=["3.0", "3.1"],
        default="3.1",
        help="Choose openapi version used in API. Default 3.1. Options are: 3.0, 3.1.",
    )

    args = parser.parse_args()
    # Parse out base_path for conveience
    args.base_path = urlsplit(args.url).path or "/"

    return args


def set_up_schemathesis(args):
    """Set up schemathesis."""
    if args.openapi_version == "3.1":
        schemathesis.experimental.OPEN_API_3_1.enable()
    return schemathesis.from_uri(args.openapi, base_url=args.url)


args = parse_args()
schema = set_up_schemathesis(args)


def set_up_logging(args, logfile=None) -> logging.Logger:
    """Set up logging."""
    loglevel = logging.WARNING

    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    # File
    if logfile is not None:
        try:
            with open(file=logfile, mode="w", encoding="utf-8") as f:
                f.write(
                    f"SEDR version {sedr_version} on python {sys.version}, schemathesis {schemathesis.__version__} \nTesting url {args.url}, openapi {args.openapi}, openapi-version {args.openapi_version}.\n\n"
                )
        except PermissionError as err:
            print(f"Could not write to logfile {logfile}: {err}\nIf you're running this as a docker container, make sure you mount the log dir (docker run -v host-dir:container-dir) and give log option to sedr using the container-dir (--log-file /container-dir/debug.log).")
            sys.exit(1)

        fh = logging.FileHandler(mode="a", filename=logfile)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    # Console
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(loglevel)
    logger.addHandler(stdout_handler)

    return logger


@schema.parametrize()  # parametrize => Create tests for all operations in schema
@settings(max_examples=args.iterations)
def test_api(case):
    """Run schemathesis standard tests."""
    try:
        case.call_and_validate()
    except schemathesis.exceptions.CheckFailed as err:
        raise AssertionError(
            f"Request to {case.base_url + case.formatted_path} failed: {', '.join(err.causes[0].args)}. Check debug log for more info."
        ) from err


@schemathesis.hook
def after_call(self, response, case):
    """Hook runs after any call to the API."""
    if case.request:
        # Log calls with status
        logger.debug(
            "after_call URL %s gave %s - %s",
            case.request.path_url,
            case.status_code,
            case.text[0:150],
        )


@schema.include(path_regex="^" + args.base_path + "$").parametrize()
@settings(max_examples=args.iterations)
def test_landingpage(case):
    """Test that the landing page contains required elements."""
    spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_7c772474-7037-41c9-88ca-5c7e95235389"
    response = case.call()

    assert (
        response.status_code < 400
    ), f"Expected status code 200 but got {response.status_code}. See {spec_ref} for more info."

    landingpage_json = None
    try:
        landingpage_json = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        logger.error("Landing page is not valid JSON.")
        raise AssertionError(
            f"Expected valid JSON but got {e}. See {spec_ref} for more info."
        ) from e

    if "title" not in landingpage_json:
        logger.warning("Landing page does not contain a title.")
    if "description" not in landingpage_json:
        logger.warning("Landing page does not contain a description.")
    assert (
        "links" in landingpage_json
    ), "Landing page does not contain links. See {spec_ref} for more info."
    for link in landingpage_json["links"]:
        assert isinstance(
            link, dict
        ), f"Link {link} is not a dictionary. See {spec_ref} for more info."
        assert (
            "href" in link
        ), f"Link {link} does not have a href attribute. See {spec_ref} for more info."
        assert (
            "rel" in link
        ), f"Link {link} does not have a rel attribute. See {spec_ref} for more info."

    logger.debug("Landingpage %s tested OK", response.url)


@schema.include(path_regex="^" + args.base_path + "conformance").parametrize()
@settings(max_examples=args.iterations)
def test_conformance(case):
    """Test that the conformance links are valid."""
    spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_4129e3d3-9428-4e91-9bfc-645405ed2369"
    response = case.call()
    conformance_json = json.loads(response.text)

    assert (
        "conformsTo" in conformance_json
    ), f"Conformance page /conformance does not contain a conformsTo attribute. See {spec_ref} for more info."

    for link in conformance_json["conformsTo"]:
        resp = None
        try:
            resp = requests.head(url=link, timeout=10)
        except requests.exceptions.MissingSchema as error:
            raise AssertionError(
                f"Link <{link}> from /conformance is malformed: {error})."
            ) from error
        assert (
            resp.status_code < 400
        ), f"Link {link} from /conformance is broken (gives status code {resp.status_code})."

    logger.debug("Conformance %s tested OK", response.url)


@schema.parametrize()
@settings(max_examples=args.iterations)
def test_collections(case):
    """The default testing in function test_api() will fuzz the collections. This function will test that collections contain EDR spesifics."""
    global collection_ids, extents

    if not case.path.endswith("/collections"):
        return

    response = case.call()
    spec_ref = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_ed0b4d0d-f90a-4a7d-a123-17a1d7849b2d"

    assert "collections" in json.loads(
        response.text
    ), f"/collections does not contain a collections attribute. See {spec_ref} for more info."

    for collection in json.loads(response.text)["collections"]:
        collection_url = collection["links"][0]["href"]

        collection_ids[collection_url] = collection["id"]
        logger.debug("test_collections found collection id %s", collection["id"])

        extent = None
        try:
            extent = collection["extent"]["spatial"]["bbox"][
                0
            ]  # TODO: assuming only one extent

            # Make sure bbox contains a list of extents, not just an extent
            assert isinstance(
                extent, list
            ), f"Extent→spatial→bbox should be a list of bboxes, not a single bbox. \
                Example [[1, 2, 3, 4], [5, 6, 7, 8]]. Was <{collection['extent']['spatial']['bbox']}>. See {spec_ref} for more info."
            extents[collection_url] = tuple(extent)

            logger.debug(
                "test_collections found extent for %s: %s", collection_url, extent
            )
        except AttributeError as err:
            pass
        except KeyError as err:
            if err.args[0] == "extent":
                raise AssertionError(
                    f"Unable to find extent for collection ID {collection['id']}. Found [{', '.join(collection.keys())}]. See {spec_ref} for more info."
                ) from err

    logger.debug("Collections %s tested OK", response.url)


@schema.parametrize()
@settings(max_examples=args.iterations)
def test_positions(case):
    """The default test in function test_api() will fuzz the coordinates. This function will test response given by coords inside and outside of the extent."""
    if not case.path.endswith("/position"):
        return

    response = case.call()
    point = None
    try:
        point = wkt_loads(case.query["coords"])
    except shapely.errors.GEOSException:
        # Invalid points are already tested by test_api, so not testing here
        return

    extent_coords = extents[case.base_url + str(case.path).removesuffix("position")]
    extent = shapely.geometry.Polygon(
        [
            (extent_coords[0], extent_coords[1]),
            (extent_coords[0], extent_coords[3]),
            (extent_coords[2], extent_coords[3]),
            (extent_coords[2], extent_coords[1]),
        ]
    )
    if extent.contains(point):
        logger.debug(
            "test_WKT Testing value INSIDE of extent, %s", case.query["coords"]
        )
        # Assert that the HTTP status code is 200
        assert (
            response.status_code == 200
        ), f"Expected status code 200 but got {response.status_code}"
    else:
        logger.debug(
            "test_WKT Testing value OUTSIDE of extent, %s", case.query["coords"]
        )
        assert (
            response.status_code != 200
        ), f"Expected status code 422 but got {response.status_code}"

    logger.debug("Positions %s tested OK", response.url)


@schema.parametrize()
@settings(max_examples=args.iterations)
def test_locations(case):
    """The default test in function test_api() will fuzz parameters. This function can test .../locations for EDR speicifics."""
    if not case.path.endswith("/locations"):
        return

    response = case.call()
    parse_locations(response.text)

    logger.debug("Locations %s tested OK", response.url)


def parse_locations(jsondata):
    """Parse locations from JSON, test geometries."""
    try:
        _ = json.loads(jsondata)
    except json.JSONDecodeError as e:
        raise AssertionError(f"parse_locations: Invalid JSON from {jsondata}") from e

    assert "name" in json.loads(
        jsondata
    ), 'Expected "name": "locations" in /locations, didn\'t find "name".'
    assert (
        "locations" in json.loads(jsondata)["name"]
    ), 'Expected "name": "locations" key in /locations, didn\'t find "locations".'
    assert "features" in json.loads(jsondata), 'Expected "features" in /locations.'

    for feature in json.loads(jsondata)["features"]:
        if feature["geometry"]["type"] == "Point":
            _ = shapely.Point(feature["geometry"]["coordinates"])
        elif feature["geometry"]["type"] == "Polygon":
            _ = shapely.Polygon(feature["geometry"]["coordinates"])
        else:
            raise AssertionError(
                f"Unable to create geometry type {feature['geometry']['type']} from coords {feature['geometry']['coordinates']}"
            )


logger = set_up_logging(args=args, logfile=args.log_file)

# /collections is tested by default, if it exists. Adding this to require it to exist
get_collections = schema["/collections"]["GET"]


if __name__ == "__main__":
    pytest.main(["-rA", "--show-capture=no", __file__])
