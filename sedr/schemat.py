__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import sys
import json
import schemathesis
from schemathesis.specs.openapi.schemas import BaseOpenAPISchema
from hypothesis import settings
from shapely.wkt import loads as wkt_loads
import pytest
import requests
from urllib.parse import urljoin
import pytest
import util
import edreq12 as edreq

import data_queries as dq

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"


def set_up_schemathesis(args, landing_page_links) -> BaseOpenAPISchema:
    """Set up schemathesis. file_path is only used for testing."""
    if args.openapi_version == "3.1":
        schemathesis.experimental.OPEN_API_3_1.enable()

    # Attempt to find schema URL automatically, if not manually set.
    if args.openapi == "":
        args.openapi = next(
        (link["href"] for link in landing_page_links if link["rel"] == "service-desc"),
        "",
    )
    if len(args.openapi) == 0:
        raise AssertionError(
            "Unable to find openapi spec for API. Please supply manually with --openapi <url>"
        )
    util.logger.info("Found openapi spec: %s", util.args.openapi)

    util.logger.info("Using EDR version %s", edreq.edr_version)

    if args.openapi.startswith("http"):
        util.logger.info(
            "Testing site %s using OpenAPI spec <%s>", args.base_url, args.openapi
        )
        return schemathesis.from_uri(uri=args.openapi, base_url=args.base_url)

    util.logger.info(
        "Testing site %s using local OpenAPI spec at path <%s>",
        args.base_url,
        args.openapi,
    )
    return schemathesis.from_path(path=util.args.openapi, base_url=args.base_url)


def set_up_collections(landing_page_links: list) -> list:
    """Get list of collections from /collections endpoint."""
    collections_url = next(
        (link.get("href") for link in landing_page_links if link.get("rel") == "data"),
        None,
    )
    if not collections_url:
        raise AssertionError(
            f"Unable to find collections url for the API through a link object with 'rel: data' in the links list: {landing_page_links}. Aborting."
        )
    try:
        response = requests.get(collections_url)
        response.raise_for_status()
        return response.json().get("collections", [])
    except (requests.RequestException, json.JSONDecodeError, requests.HTTPError) as err:
        util.logger.error("Error fetching collections <%s>:\n%s", collections_url, err)
        return []


landing_page_links = util.fetch_landing_page_links(util.args.url)

# Global variables
schema = set_up_schemathesis(util.args, landing_page_links)
collections = set_up_collections(landing_page_links)


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


@pytest.mark.parametrize("id,collection", [(c["id"], c) for c in collections])
def test_edr_collections(id, collection):
    """The default testing in function test_api() will fuzz the collections.
    This function will test that collections contain EDR spesifics.
    """

    spec_ref = f"{edreq.edr_root_url}#_second_tier_collections_tests"

    # Run edr, ogc, profile tests
    for test_func in util.test_functions["collection"]:
        status, msg = test_func(jsondata=collection)
        if not status:
            util.logger.error(
                "Test %s failed with message: %s", test_func.__name__, msg
            )
            raise AssertionError(
                f"Test {test_func.__name__} failed with message: {msg}"
            )
        util.logger.info("Test %s passed. (%s)", test_func.__name__, msg)


@pytest.mark.parametrize("id,collection", [(c["id"], c) for c in collections])
def test_data_query_response(id, collection):
    """Test that data queries work as expected and that the response is correct.
    For each data query type in each collection, perform one query inside spatial extent
    and one query outside spatial extent.
    """

    try:
        extent = util.parse_spatial_bbox(collection)
    except Exception as err:
        pytest.fail(
            f"Extent in collection {id}> is not valid because: {err}...Skipping this test."
        )

    base_url = collection_url(collection["links"])
    for query_type in collection["data_queries"]:
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
            continue

        try:
            if queries.outside != "":
                outside = requests.get(queries.outside)
                if outside.status_code < 400 or outside.status_code >= 500:
                    pytest.fail(
                        f"Expected status code 4xx for query {queries.outside}; Got {outside.status_code}"
                    )
            inside = requests.get(queries.inside)
        except requests.exceptions.RequestException as err:
            pytest.fail(f"Request for {err.request.url} failed: {err}")
        if inside.status_code != 200:
            pytest.fail(
                f"Expected status code 200 for query {queries.inside}; Got {inside.status_code}"
            )

        for test_func in util.test_functions["data_query_response"]:
            status, msg = test_func(jsondata=inside.json())
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
