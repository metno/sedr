import sys
import logging
import schemathesis
import argparse
import json
from urllib.parse import urlsplit
import shapely


__version__ = "v0.7.1"
edr_version = "1.1"


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
    openapi_version_choices = ["3.1"] # "3.0", "3.1"
    parser.add_argument(
        "--openapi-version",
        choices=openapi_version_choices,
        default="3.1",
        help=f"Choose openapi version used in API. Default 3.1. Options are: {openapi_version_choices}",
    )

    args = parser.parse_args()
    # Parse out base_path for conveience
    args.base_path = urlsplit(args.url).path or "/"

    return args


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
                    f"SEDR version {__version__} on python {sys.version}, schemathesis "
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


args = parse_args()
logger = set_up_logging(args=args, logfile=args.log_file)
