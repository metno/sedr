__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import os
import sys
import json
import schemathesis
from schemathesis.specs.openapi.schemas import BaseOpenAPISchema
from hypothesis import settings
import shapely
from shapely.wkt import loads as wkt_loads
import pytest
import requests
from urllib.parse import urljoin, urlencode

import util
import edreq12 as edreq

import data_queries as dq

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"


# Globals
schema = None
collections = []


def set_up_schemathesis(args) -> BaseOpenAPISchema:
    """Set up schemathesis. file_path is only used for testing."""
    if args.openapi_version == "3.1":
        schemathesis.experimental.OPEN_API_3_1.enable()

    if args.openapi == "":
        # Attempt to find schema URL automatically
        args.openapi = util.locate_openapi_url(args.url, timeout=util.args.timeout)
        if len(args.openapi) == 0:
            raise AssertionError(
                "Unable to find openapi spec for API. Please supply manually with --openapi <url>"
            )
        util.logger.info("Found openapi spec: %s", util.args.openapi)

    util.logger.info("Using EDR version %s", edreq.edr_version)

    if args.openapi.startswith("http"):
        util.logger.info(
            "Testing site %s using OpenAPI spec <%s>", args.url, args.openapi
        )
        return schemathesis.from_uri(uri=args.openapi, base_url=args.url)

    util.logger.info(
        "Testing site %s using local OpenAPI spec at path <%s>", args.url, args.openapi
    )
    return schemathesis.from_path(path=util.args.openapi, base_url=args.url)


try:
    schema = set_up_schemathesis(util.args)
except requests.exceptions.ConnectionError:
    msg = f"Unable to connect to site <{util.args.url}>"
    pytest.fail(msg)


@schema.parametrize()  # parametrize => Create tests for all operations in schema
@settings(max_examples=util.args.iterations, deadline=None)
def test_openapi(case):
    """Run schemathesis standard tests."""
    try:
        case.call_and_validate()
    except schemathesis.exceptions.CheckFailed as err:
        # raise AssertionError(
        causes = None
        if err is not None and err.causes is not None:
            causes = ", ".join(err.causes[0].args)
        else:
            pass
        print(
            f"Request to {case.base_url + case.formatted_path} failed: {causes}. Check debug log for more info.",
            file=sys.stderr,
        )
        # ) from err


@schemathesis.hook
def after_call(context, case, response):  # noqa: pylint: disable=unused-argument
    """Hook runs after any call to the API, used for logging."""
    if response.request:
        # Log calls with status
        util.logger.debug(  # noqa: pylint: disable=logging-not-lazy
            f"after_call {'OK' if response.ok else 'ERR'} "
            + f"{response.request.path_url} {response.text[0:150]}"
        )


@(
    schema.include(path_regex="^" + os.path.join(util.args.base_path, "collections$"))
    .include(method="GET")
    .parametrize()
)
@settings(max_examples=util.args.iterations, deadline=None)
def test_edr_collections(case):
    """The default testing in function test_api() will fuzz the collections.
    This function will test that collections contain EDR spesifics.
    """
    global collections  # NOQA

    response = case.call()
    spec_ref = f"{edreq.edr_root_url}#_second_tier_collections_tests"

    assert "collections" in json.loads(response.text), (
        f"/collections does not contain a collections attribute. See {spec_ref} for more info."
    )

    for collection_json in json.loads(response.text)["collections"]:
        # Use url as key for extents. Remove trailing slash from url.
        collection_url = util.parse_collection_url(collection_json)

        # Run edr, ogc, profile tests
        for test_func in util.test_functions["collection"]:
            status, msg = test_func(jsondata=collection_json)
            if not status:
                util.logger.error(
                    "Test %s failed with message: %s", test_func.__name__, msg
                )
                raise AssertionError(
                    f"Test {test_func.__name__} failed with message: {msg}"
                )
            util.logger.info("Test %s passed. (%s)", test_func.__name__, msg)

        collections.append(collection_json)


def test_data_query_response():
    """Test that data queries work as expected and that the response is correct.
    For each data query type in each collection, perform one query inside spatial extent
    and one query outside spatial extent.
    """
    global collections  # noqa: pylint: disable=global-variable-not-assigned

    for collection_json in collections:
        extent = util.parse_spatial_bbox(collection_json)[0]
        base_url = collection_url(collection_json["links"])

        for query_type in collection_json["data_queries"]:
            queries = None
            match query_type:
                case "position":
                    queries = dq.position_queries(base_url, extent)
                case "radius":
                    queries = dq.radius_queries(base_url, extent)
                case "area":
                    queries = dq.area_queries(base_url, extent)
                case "trajectory":
                    queries = dq.trajectory_queries(base_url, extent)

            if queries is None:
                pytest.fail(
                    f"Unknown data query type {query_type} in collection {collection_json['id']}"
                )

            if queries.outside != "":
                response = requests.get(queries.outside)
                if response.status_code < 400 or response.status_code >= 500:
                    pytest.fail(
                        f"Expected status code 4xx for query {queries.outside}; Got {response.status_code}"
                    )

            response = requests.get(queries.inside)
            if response.status_code != 200:
                pytest.fail(
                    f"Expected status code 200 for query {queries.inside}; Got {response.status_code}"
                )

            for test_func in util.test_functions["data_query_response"]:
                status, msg = test_func(jsondata=response.json())
                if not status:
                    util.logger.error(
                        "Test %s failed with message: %s", test_func.__name__, msg
                    )
                    raise AssertionError(
                        f"Test {test_func.__name__} failed with message: {msg}"
                    )
                util.logger.info("Test %s passed. (%s)", test_func.__name__, msg)


def collection_url(links):
    collection_link = next((x for x in links if x["rel"] == "data"), None)

    if collection_link is None:
        pytest.fail(f"Expected link with rel=self to be present: {links}")

    url = collection_link["href"]
    if str.endswith("/", url):
        return url

    return url + "/"
