import os
import sys
import json
import schemathesis
from schemathesis.specs.openapi.schemas import BaseOpenAPISchema
from hypothesis import settings, assume
import shapely
from shapely.wkt import loads as wkt_loads
import pytest
import requests

import util
import edreq11 as edreq
import rodeoprofile10 as rodeoprofile


__author__ = "Lars Falk-Petersen"
__license__ = "GPL-3.0"


# Globals
schema = None
extents = {}
collection_ids = {}
use_rodeoprofile = False


def set_up_schemathesis(args) -> BaseOpenAPISchema:
    """Set up schemathesis. file_path is only used for testing."""
    if args.openapi_version == "3.1":
        schemathesis.experimental.OPEN_API_3_1.enable()

    if args.openapi == "":
        # Attempt to find schema URL automatically
        args.openapi = util.locate_openapi_url(args.url)
        if len(args.openapi) == 0:
            raise AssertionError(
                "Unable to find openapi spec for API. Please supply manually with --openapi <url>"
            )
        util.logger.info("Found openapi spec: %s", util.args.openapi)

    util.logger.info("Using EDR version %s", edreq.__edr_version__)

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
def after_call(context, case, response):
    """Hook runs after any call to the API, used for logging."""
    if response.request:
        # Log calls with status
        util.logger.debug(
            f"after_call {'OK' if response.ok else 'ERR'} "
            + f"{response.request.path_url} {response.text[0:150]}"
        )


@schema.include(
    path_regex="^" + os.path.join(util.args.base_path, "conformance")
).parametrize()
@settings(max_examples=util.args.iterations, deadline=None)
def test_edr_conformance(case):
    """Test /conformance endpoint."""
    global use_rodeoprofile
    response = case.call()
    conformance_json = json.loads(response.text)

    if (
        util.args.rodeo_profile
        or rodeoprofile.conformance_url in conformance_json["conformsTo"]
    ):
        use_rodeoprofile = True
        util.logger.info(
            "Including tests for Rodeo profile %s", rodeoprofile.conformance_url
        )

    if "conformsTo" not in conformance_json:
        spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_4129e3d3-9428-4e91-9bfc-645405ed2369"
        raise AssertionError(
            f"Conformance page /conformance does not contain a conformsTo attribute. See {spec_ref} for more info."
        )

    resolves, resolves_message = util.test_conformance_links(
        jsondata=conformance_json["conformsTo"]
    )
    if not resolves:
        raise AssertionError(resolves_message)

    requirementA2_2_A5, requirementA2_2_A5_message = edreq.requirementA2_2_A5(
        jsondata=conformance_json["conformsTo"], siteurl=util.args.url
    )
    if not requirementA2_2_A5:
        util.logger.error(requirementA2_2_A5_message)
        # raise AssertionError(requirementA2_2_A5_message)

    requirementA2_2_A7, requirementA2_2_A7_message = edreq.requirementA2_2_A7(
        response.raw.version
    )
    if not requirementA2_2_A7:
        raise AssertionError(requirementA2_2_A7_message)

    requirementA11_1, requirementA11_1_message = edreq.requirementA11_1(
        jsondata=conformance_json["conformsTo"]
    )
    if not requirementA11_1:
        raise AssertionError(requirementA11_1_message)

    if use_rodeoprofile:
        requirement7_1, requirement7_1_message = rodeoprofile.requirement7_1(
            jsondata=conformance_json["conformsTo"]
        )
        if not requirement7_1:
            raise AssertionError(requirement7_1_message)

    util.logger.debug("Conformance %s tested OK", response.url)


@schema.include(path_regex="^" + util.args.base_path + "$").parametrize()
@settings(max_examples=util.args.iterations, deadline=None)
def test_edr_landingpage(case):
    """Test that the landing page contains required elements."""
    spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_7c772474-7037-41c9-88ca-5c7e95235389"
    landingpage_json = None
    response = case.call()
    try:
        landingpage_json = json.loads(response.text)
        landing, landing_message = util.parse_landing_json(landingpage_json)
        if not landing:
            raise AssertionError(
                f"Landing page is missing required elements. See <{spec_ref}> for more info. {landing_message}"
            )

        util.logger.debug("Landingpage %s tested OK", response.url)
    except json.decoder.JSONDecodeError:
        util.logger.warning("Landing page is not valid JSON.")
        raise AssertionError("Landing page is not valid JSON")

    if use_rodeoprofile:
        requirement7_2, requirement7_2_message = rodeoprofile.requirement7_2(
            jsondata=landingpage_json
        )
        if not requirement7_2:
            raise AssertionError(requirement7_2_message)


@schema.include(
    path_regex="^" + os.path.join(util.args.base_path, "collections$")
).parametrize()
@settings(max_examples=util.args.iterations, deadline=None)
def test_edr_collections(case):
    """The default testing in function test_api() will fuzz the collections.
    This function will test that collections contain EDR spesifics. It will
    also require /collections to exist, in accordance with Requirement A.2.2 A.9
    <https://docs.ogc.org/is/19-086r6/19-086r6.html#_26b5ceeb-1127-4dc1-b88e-89a32d73ade9>
    """
    global collection_ids, extents

    response = case.call()
    spec_ref = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_ed0b4d0d-f90a-4a7d-a123-17a1d7849b2d"

    assert (
        "collections" in json.loads(response.text)
    ), f"/collections does not contain a collections attribute. See {spec_ref} for more info."

    for collection in json.loads(response.text)["collections"]:
        # Use url as key for extents. Remove trailing slash from url.
        collection_url = collection["links"][0]["href"].rstrip("/")

        collection_ids[collection_url] = collection["id"]
        util.logger.debug("test_collections found collection id %s", collection["id"])

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

            util.logger.debug(
                "test_collections found extent for %s: %s", collection_url, extent
            )
        except AttributeError:
            pass
        except KeyError as err:
            if err.args[0] == "extent":
                raise AssertionError(
                    f"Unable to find extent for collection ID {collection['id']}. Found [{', '.join(collection.keys())}]. See {spec_ref} for more info."
                ) from err

        if use_rodeoprofile:
            requirement7_3, requirement7_3_message = rodeoprofile.requirement7_3(
                jsondata=collection
            )
            if not requirement7_3:
                raise AssertionError(requirement7_3_message)

            requirement7_4, requirement7_4_message = rodeoprofile.requirement7_4(
                jsondata=collection
            )
            if not requirement7_4:
                raise AssertionError(requirement7_4_message)

            requirement7_5, requirement7_5_message = rodeoprofile.requirement7_5(
                jsondata=collection
            )
            if not requirement7_5:
                raise AssertionError(requirement7_5_message)


for p in schema.raw_schema["paths"].keys():
    # Optionally include endpoints if they exist, otherwise schemathesis will refuse to run
    # TODO: can perhaps be replaced with a filter?
    # https://schemathesis.readthedocs.io/en/stable/extending.html#filtering-api-operations

    # Include position_extent test
    if p.endswith("/position"):

        @schema.include(path_regex="/position$").parametrize()
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
                point = wkt_loads(case.query["coords"])
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
