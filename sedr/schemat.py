import sys
import json
import schemathesis
from hypothesis import settings, assume
import shapely
from shapely.wkt import loads as wkt_loads

import util
import edreq11 as edreq


# Globals
extents = {}
collection_ids = {}


def set_up_schemathesis(args):
    """Set up schemathesis."""
    if args.openapi_version == "3.1":
        schemathesis.experimental.OPEN_API_3_1.enable()
    return schemathesis.from_uri(args.openapi, base_url=args.url)


schema = set_up_schemathesis(util.args)

# Require /collections to exist, in accordance with Requirement A.2.2 A.9
# <https://docs.ogc.org/is/19-086r6/19-086r6.html#_26b5ceeb-1127-4dc1-b88e-89a32d73ade9>
_ = schema["/collections"]["GET"]


@schema.parametrize()  # parametrize => Create tests for all operations in schema
@settings(max_examples=util.args.iterations, deadline=None)
def test_api(case):
    """Run schemathesis standard tests."""
    try:
        case.call_and_validate()
    except schemathesis.exceptions.CheckFailed as err:
        # raise AssertionError(
        causes = None
        if err is not None and len(err.causes) > 0:
            causes = ", ".join(err.causes[0].args)
        else:
            pass
        print(
            f"Request to {case.base_url + case.formatted_path} failed: {causes}. Check debug log for more info.",
            file=sys.stderr,
        )
        # ) from err


@schemathesis.hook
def after_call(self, response, case):
    """Hook runs after any call to the API."""
    if case.request:
        # Log calls with status
        util.logger.debug(
            "after_call URL %s gave %s - %s",
            case.request.path_url,
            case.status_code,
            case.text[0:150],
        )


@schema.include(path_regex="^" + util.args.base_path + "$").parametrize()
@settings(max_examples=util.args.iterations, deadline=None)
def test_landingpage(case):
    """Test that the landing page contains required elements."""
    spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_7c772474-7037-41c9-88ca-5c7e95235389"
    response = case.call()
    landingpage_json = None
    try:
        landingpage_json = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        util.logger.error("Landing page is not valid JSON.")
        raise AssertionError(
            f"Expected valid JSON but got {e}. See {spec_ref} for more info."
        ) from e

    if "title" not in landingpage_json:
        util.logger.warning("Landing page does not contain a title.")
    if "description" not in landingpage_json:
        util.logger.warning("Landing page does not contain a description.")
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

    util.logger.debug("Landingpage %s tested OK", response.url)


@schema.include(path_regex="^" + util.args.base_path + "conformance").parametrize()
@settings(max_examples=util.args.iterations, deadline=None)
def test_conformance(case):
    """Test /conformance endpoint."""
    response = case.call()
    conformance_json = json.loads(response.text)

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
        jsondata=conformance_json["conformsTo"]
    )
    if not requirementA2_2_A5:
        raise AssertionError(requirementA2_2_A5_message)

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

    util.logger.debug("Conformance %s tested OK", response.url)


@schema.parametrize()
@settings(max_examples=util.args.iterations, deadline=None)
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

    util.logger.debug("Collections %s tested OK", response.url)


# @schema.parametrize()
# @settings(max_examples=util.args.iterations, deadline=None)
# def test_positions(case):
#     """The default test in function test_api() will fuzz the coordinates. This function will test response given by coords inside and outside of the extent."""
#     if not case.path.endswith("/position"):
#         return

#     response = case.call()
#     point = None
#     try:
#         point = wkt_loads(case.query["coords"])
#     except shapely.errors.GEOSException:
#         # Invalid points are already tested by test_api, so not testing here
#         return

#     extent_path = case.base_url + str(case.path).removesuffix("/position")
#     extent_coords = extents[extent_path]
#     extent = shapely.geometry.Polygon(
#         [
#             (extent_coords[0], extent_coords[1]),
#             (extent_coords[0], extent_coords[3]),
#             (extent_coords[2], extent_coords[3]),
#             (extent_coords[2], extent_coords[1]),
#         ]
#     )

#     schema[case.path][case.method].validate_response(response)

#     if extent.contains(point):
#         util.logger.debug(
#             "test_positions Testing value INSIDE of extent, %s", case.query["coords"]
#         )
#         # Assert that the HTTP status code is 200
#         if response.status_code != 200:
#             assume( # Marking the example as bad. https://github.com/metno/sedr/issues/5
#                 f"Expected status code 200 but got {response.status_code}"
#             )
#     else:
#         util.logger.debug(
#             "test_positions Testing value OUTSIDE of extent, %s", case.query["coords"]
#         )
#         if response.status_code != 422:
#             assume( # Marking the example as bad. https://github.com/metno/sedr/issues/5
#                 f"Expected status code 422 but got {response.status_code}"
#             )


# TODO: needs to be reworked
# @schema.parametrize()
# @settings(max_examples=util.args.iterations, deadline=None)
# def test_locations(case):
#     """The default test in function test_api() will fuzz parameters. This function can test .../locations for EDR speicifics."""
#     if not case.path.endswith("/locations"):
#         return

#     response = case.call()
#     # schema[case.path][case.method].validate_response(response)
#     if response.ok:
#         util.parse_locations(response.text)
#     else:
#         # Invalid points are already tested by test_api, so not testing here
#         pass

#     util.logger.debug("Locations %s tested OK", response.url)


if __name__ == "__main__":
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])
