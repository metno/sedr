__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

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
        default=True,
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
    # Parse out base_path for convenience
    args.base_path = urlsplit(args.url).path or "/"
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
        logger.debug(  # noqa: pylint: disable=logging-not-lazy
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


def locate_openapi_url(url: str, timeout: int) -> str:
    """Locate the OpenAPI URL based on main URL."""
    request = requests.get(url, timeout=timeout)

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


def build_conformance_url(url: str) -> str:
    """Build the conformance URL based on main URL."""
    return urljoin(url, "/conformance")


def parse_collection_url(jsondata: dict) -> str:
    return jsondata["links"][0]["href"].rstrip("/")


def parse_spatial_bbox(jsondata: dict) -> list:
    try:
        return jsondata["extent"]["spatial"]["bbox"]
    except (AttributeError, KeyError) as err:
        return []
