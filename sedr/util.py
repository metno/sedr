import sys
import logging
import requests
import schemathesis
import argparse
import json
from urllib.parse import urlsplit


__author__ = "Lars Falk-Petersen"
__license__ = "GPL-3.0"

args = logger = None


def parse_args(args, version: str = "") -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="schemathesis-edr")
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument(
        "--openapi",
        type=str,
        help="URL or path to openapi spec for API",
        default="",
    )
    parser.add_argument("--url", type=str, help="URL to API", default="")
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Amount of examples to generate, per test. Default 10. Increase for local, developer testing.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Log output",
    )
    openapi_version_choices = ["3.1"]  # "3.0", "3.1"
    parser.add_argument(
        "--openapi-version",
        choices=openapi_version_choices,
        default="3.1",
        help=f"Choose openapi version used in API. Default 3.1. Options are: {openapi_version_choices}",
    )
    parser.add_argument(
        "--rodeo-profile",
        action="store_true",
        default=False,
        help="Use the rodeo profile even though the API doesn't specify it. Default False.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat SHOULD in any profile as SHALL. Default False.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Set timeout for requests. Default 10.",
    )

    args = parser.parse_args(args)
    # Parse out base_path for convenience
    args.base_path = urlsplit(args.url).path or "/"
    return args


def set_up_logging(args, logfile=None, version: str = "") -> logging.Logger:
    """Set up logging."""
    loglevel = logging.WARNING

    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    # File
    if logfile is not None:
        try:
            with open(file=logfile, mode="w", encoding="utf-8") as f:
                f.write(
                    f"SEDR version {version} on python {sys.version}, schemathesis "
                    + f"{schemathesis.__version__} \nTesting url {args.url}, openapi {args.openapi}, "
                    + f"openapi-version {args.openapi_version}.\n\n"
                )
        except PermissionError as err:
            print(
                f"Could not write to logfile {logfile}: {err}\nIf you're running this as a docker "
                + "container, make sure you mount the log dir (docker run -v host-dir:container-dir) "
                + "and give log option to sedr using the container-dir (--log-file /container-dir/debug.log)."
            )
            sys.exit(1)

        fh = logging.FileHandler(mode="a", filename=logfile)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    # Console
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(loglevel)
    logger.addHandler(stdout_handler)

    return logger


def parse_locations(jsondata) -> None:
    """Parse locations from JSON, test geometries."""
    try:
        _ = json.loads(jsondata)
    except json.JSONDecodeError as e:
        raise AssertionError(f"parse_locations: Invalid JSON from {jsondata}") from e

    # TODO: Locations must be a FeatureCollection or a location.
    # https://docs.ogc.org/is/19-086r6/19-086r6.html#rc_locations-section

    # if "name" not in json.loads(jsondata):
    #     raise AssertionError('Expected "name": "locations" in /locations, didn\'t find "name".')
    # if "locations" not in json.loads(jsondata)["name"]:
    #     raise AssertionError('Expected "name": "locations" in /locations, didn\'t find "locations".')

    # assert "features" in json.loads(jsondata), 'Expected "features" in /locations.'

    # for feature in json.loads(jsondata)["features"]:
    #     if feature["geometry"]["type"] == "Point":
    #         _ = shapely.Point(feature["geometry"]["coordinates"])
    #     elif feature["geometry"]["type"] == "Polygon":
    #         _ = shapely.Polygon(feature["geometry"]["coordinates"])
    #     else:
    #         raise AssertionError(
    #             f"Unable to create geometry type {feature['geometry']['type']} from coords {feature['geometry']['coordinates']}"
    #         )


def test_conformance_links(jsondata) -> tuple[bool, str]:  # pylint: disable=unused-argument
    """Test that all conformance links are valid and resolves.

    TODO: http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections doesn't work, so postponing this.
    """
    # for link in conformance_json["conformsTo"]:
    #     resp = None
    #     try:
    #         resp = requests.head(url=link, timeout=10)
    #     except requests.exceptions.MissingSchema as error:
    #         raise AssertionError(
    #             f"Link <{link}> from /conformance is malformed: {error})."
    #         ) from error
    #     assert (
    #         resp.status_code < 400
    #     ), f"Link {link} from /conformance is broken (gives status code {resp.status_code})."
    return True, ""


def locate_openapi_url(url: str) -> str:
    """Locate the OpenAPI URL based on main URL."""
    request = requests.get(url, timeout=10)

    # Json
    # See https://github.com/metno/sedr/issues/6
    try:
        if request.json():
            for link in request.json()["links"]:
                if link["rel"] == "service-desc":
                    return link["href"]
    except json.JSONDecodeError:
        pass

    # TODO:
    # Html
    # Yaml
    # Xml
    return ""
