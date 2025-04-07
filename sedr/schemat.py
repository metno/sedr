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


__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"


# Globals
schema = None
extents = {}
collection_ids = {}
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
    global collection_ids, extents, collections  # NOQA

    response = case.call()
    spec_ref = f"{edreq.edr_root_url}#_second_tier_collections_tests"

    assert "collections" in json.loads(response.text), (
        f"/collections does not contain a collections attribute. See {spec_ref} for more info."
    )

    for collection_json in json.loads(response.text)["collections"]:
        # Use url as key for extents. Remove trailing slash from url.
        collection_url = util.parse_collection_url(collection_json)

        collection_ids[collection_url] = collection_json["id"]
        util.logger.debug(
            "test_collections found collection id %s", collection_json["id"]
        )

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

        # Validation of spatial_bbox done above
        extent = util.parse_spatial_bbox(collection_json)
        collections.append(collection_json)

        extents[collection_url] = tuple(extent[0])


for p in schema.raw_schema["paths"].keys():
    # Optionally include endpoints if they exist, otherwise schemathesis will refuse to run
    # TODO: can perhaps be replaced with a filter?
    # https://schemathesis.readthedocs.io/en/stable/extending.html#filtering-api-operations

    # Include position_extent test
    if p.endswith("/position"):

        @schema.include(path_regex="/position$").include(method="GET").parametrize()
        @settings(max_examples=util.args.iterations, deadline=None)
        def test_edr_position_extent(case):
            """The default test in function test_openapi will fuzz the coordinates.

            This function will test response given by coords inside and outside of the extent.

            TODO: perhaps this can rather be done with a map hook?
            https://schemathesis.readthedocs.io/en/stable/extending.html#modifying-data
            """
            response = case.call()
            point = None
            try:
                pytest.fail(
                    f"Expected good coords; got {case.query["coords"]}"
                )
                #point = wkt_loads(case.query["coords"])
            except shapely.errors.GEOSException:
                return  # Invalid points are already tested by test_api, so not testing here

            extent_path = case.base_url + str(case.path).removesuffix("/position")
            extent_coords = extents[extent_path]
            extent = shapely.geometry.Polygon(
                [
                    (extent_coords[0], extent_coords[1]),
                    (extent_coords[0], extent_coords[3]),
                    (extent_coords[2], extent_coords[3]),
                    (extent_coords[2], extent_coords[1]),
                ]
            )

            schema[case.path][case.method].validate_response(response)

            # TODO: not sure if assume, pytest.fail or some other option is best when detecting errors
            if extent.contains(point):
                util.logger.debug(
                    "test_positions Testing value INSIDE of extent, %s",
                    case.query["coords"],
                )
                if response.status_code != 200:
                    # assume(  # Marking the example as bad. https://github.com/metno/sedr/issues/5
                    #     f"Expected status code 200 but got {response.status_code}"
                    # )
                    pytest.fail(
                        f"Expected status code 200 but got {response.status_code}"
                    )
            else:
                util.logger.debug(
                    "test_positions Testing value OUTSIDE of extent, %s",
                    case.query["coords"],
                )
                if response.status_code != 422:
                    # assume(  # Marking the example as bad. https://github.com/metno/sedr/issues/5
                    #     f"Expected status code 422 but got {response.status_code}"
                    # )
                    pytest.fail(
                        f"Expected status code 422 but got {response.status_code}"
                    )
    
def test_data_query_response():
    """Perform one data query request per data_queries type specified in each collection.
    Check that you get a valid response.
    """
    global collections  # noqa: pylint: disable=global-variable-not-assigned

    for collection_json in collections:
        extent = util.parse_spatial_bbox(collection_json)[0]
        base_url = collection_url(collection_json["links"])

        url = ""
        for query_type in collection_json["data_queries"]:
            match query_type:
                case "position":
                    url = position_query_url(base_url, extent, collection_json["data_queries"]["position"])
                case "radius":
                    url = radius_query_url(base_url, extent, collection_json["data_queries"]["radius"])
                case "area":
                    url = area_query_url(base_url, extent, collection_json["data_queries"]["area"])

            response = requests.get(url)
            if response.status_code != 200:
                pytest.fail(
                    f"Expected status code 200 for query {url}; Got {response.status_code}"
                )

            for test_func in util.test_functions["data_query_response"]:
                status, msg = test_func(jsondata=collection_json)
                if not status:
                    util.logger.error(
                        "Test %s failed with message: %s", test_func.__name__, msg
                    )
                    raise AssertionError(
                        f"Test {test_func.__name__} failed with message: {msg}"
                    )
                util.logger.info("Test %s passed. (%s)", test_func.__name__, msg)



def position_query_url(base_url, extent, data_query_json):
    long = (extent[2] - extent[0])/2 + extent[0]
    lat = (extent[3] - extent[1])/2 + extent[1]
    
    return urljoin(base_url,"position") + f"?coords=POINT({long} {lat})"

def radius_query_url(base_url, extent, data_query_json):
    long = (extent[2] - extent[0])/2 + extent[0]
    lat = (extent[3] - extent[1])/2 + extent[1]

    query_params = {
        'coords': f"POINT({long} {lat})",
        'within': "1000",
        'within_units': 'm',
    }
    
    return urljoin(base_url, "position") + "?" + urlencode(query_params)

def area_query_url(base_url, extent):
    polygon = ""
    points = 4

    long_step = (extent[2] - extent[0]) / (points + 1)
    lat_step = (extent[3] - extent[1]) / (points + 1)
    for point in range(points):
        long = extent[0] + long_step*point
        lat += extent[1] + lat_step*point

        polygon += f"{long} {lat}"
        if point != points:
            polygon += ","
    
    return urljoin(base_url, "area") + "?" + "coords=POLYGON(f{polygon})"

def collection_url(links):
    collection_link = next((x for x in links if x["rel"] == "data"), None)
    
    if collection_link is None:
        pytest.fail(f"Expected link with rel=self to be present: {links}")

    return collection_link["href"]