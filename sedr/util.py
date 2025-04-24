import sys
import logging
import requests
import schemathesis
import argparse
import json
from typing import List, Callable, Dict
from urllib.parse import urljoin, urlsplit
from rich.logging import RichHandler

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

args = logger = None
test_functions: Dict[str, List[Callable]] = {
    "landing": [],
    "conformance": [],
    "collection": [],
}


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
    parser.add_argument("--url", type=str, help="URL to API", required=True)
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
        "--rodeo-profile-core",
        action="store_true",
        default=True,
        help="Use the rodeo profile core conformance class even though the API doesn't specify it. Default False.",
    )
    parser.add_argument(
        "--rodeo-profile-insitu-observations",
        action="store_true",
        default=False,
        help="Use the rodeo profile core conformance class even though the API doesn't specify it. Default False.",
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
    # Set base_path and base_url for convenience. Ensure they end with /.
    # Use these to build URLs for requests.
    args.base_path = urlsplit(args.url).path.rstrip("/") + "/"
    args.base_url = args.url.rstrip("/") + "/"
    return args


def set_up_logging(args, logfile=None, version: str = "") -> logging.Logger:
    """Set up logging."""
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    FORMAT = "%(asctime)s - %(message)s"
    logging.getLogger("requests").setLevel(logging.WARNING)

    # File
    if logfile is not None:
        try:
            with open(file=logfile, mode="w", encoding="utf-8") as _:
                pass  # Touch file
        except PermissionError as err:
            print(
                f"Could not write to logfile {logfile}: {err}\nIf you're "
                f"running this as a docker container, make sure you mount "
                f"the log dir (docker run -v host-dir:container-dir) and give "
                f"log option to sedr using the container-dir "
                f"(--log-file /container-dir/debug.log)."
            )
            sys.exit(1)

        fh = logging.FileHandler(mode="a", filename=logfile)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(FORMAT, datefmt="[%X]"))
        logger.addHandler(fh)
        logger.debug(  # pylint:disable=logging-fstring-interpolation,logging-not-lazy
            f"SEDR version {version} on python {sys.version}, schemathesis "
            f"{schemathesis.__version__} \nTesting url <{args.url}>, openapi "
            f"url <{args.openapi}>, openapi-version {args.openapi_version}.\n"
        )

    # Console
    stdout_handler = RichHandler(level=logging.INFO)
    stdout_handler.setFormatter(logging.Formatter(FORMAT, datefmt="[%X]"))
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


def fetch_landing_page_links(url: str, timeout=10) -> list:
    """Fetch landing page links."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json().get("links", [])
    except (requests.RequestException, json.JSONDecodeError, requests.HTTPError) as err:
        logger.error("Error fetching landing page <%s>:\n%s", url, err)
        return []


def build_conformance_url(url: str) -> str:
    """Build the conformance URL based on main URL."""
    return urljoin(url, "conformance")


def parse_spatial_bbox(jsondata: dict) -> list:
    try:
        extent = jsondata["extent"]["spatial"]["bbox"]
        if (
            len(extent) != 1
            or not isinstance(extent, list)
            or not all(isinstance(coord, (int, float)) for coord in extent[0])
        ):
            raise AssertionError(
                f"Extent→spatial→bbox should be a list of bboxes with exactly "
                f"one bbox in, found {len(extent)}"
            )
    except (AttributeError, KeyError):
        raise AssertionError("parse_spatial_bbox: Unable to find extent in JSON data.")

    return extent[0]


def get_collections(landing_page_links: list) -> list:
    """Get list of collections from /collections endpoint."""
    collections_url = next(
        (link.get("href") for link in landing_page_links if link.get("rel") == "data"),
        None,
    )
    if not collections_url:
        logger.error("No collections URL found")
        return []
    try:
        response = requests.get(collections_url)
        response.raise_for_status()
        return response.json().get("collections", [])
    except (requests.RequestException, json.JSONDecodeError, requests.HTTPError) as err:
        logger.error("Error fetching collections <%s>:\n%s", collections_url, err)
        return []
