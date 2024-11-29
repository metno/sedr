"""EDR requirements."""

from collections.abc import Callable
import util

edr_version = "1.2"
edr_root_url = "https://docs.ogc.org/DRAFTS/19-086r7.html"
ogc_api_common_url = "https://docs.ogc.org/is/19-072/19-072.html"
conformance_urls = [
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
    "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/core",  # Assume this will be changed to edr_version
]
openapi_conformance_urls = [
    "http://www.opengis.net/spec/ogcapi-edr-1/1.1/req/oas30",  # Assume this will be changed to oas31
    "http://www.opengis.net/spec/ogcapi-edr-1/1.2/req/oas31",
]


def requirementA2_2_A5(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.2
    Requirement Annex A2.2 A5

    Check if the conformance page contains the required EDR classes.
    jsondata should be the "conformsTo"-part of the conformance page.
    """
    spec_url = f"{edr_root_url}#req_core_conformance"

    if "conformsTo" not in jsondata:
        return False, (
            f"Conformance page does not contain a "
            f"conformsTo attribute. See <{spec_url}> for more info."
        )

    for url in conformance_urls:
        if url not in jsondata["conformsTo"]:
            return False, (
                f"Conformance page does not contain "
                f"the core edr class {url}. See <{spec_url}> for more info."
            )

    return True, "Conformance page contains the required EDR classes."


def requirementA11_1(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.1
    Requirement A11.1

    Check if the conformance page contains openapi classes,
    and that they match our version."""
    spec_url = f"{edr_root_url}#_requirements_class_openapi_3_0"

    for url in jsondata["conformsTo"]:
        if url in openapi_conformance_urls:
            if (
                "oas31" in url or "oas30" in url  # TODO: oas30 should be removed
            ):
                return True, f"Found openapi class <{url}>. "
            return (
                False,
                f"OpenAPI version {util.args.openapi_version} and version in "
                f"conformance {url} doesn't match. See <{spec_url}> for more info.",
            )

    return (
        False,
        f"Conformance page /conformance does not contain an openapi class. "
        f"See <{spec_url}> for more info.",
    )


def requrementA5_2(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.2
    Requirement A5.2

    Check extent spatial bbox
    """

    spec_url = f"{edr_root_url}#req_core_rc-bbox-definition"

    extent = None
    extent = util.parse_spatial_bbox(jsondata)
    if extent is None or len(extent) > 1 or not isinstance(extent, list):
        return (
            False,
            f"Extent→spatial→bbox should be a list of bboxes with exactly "
            f"one bbox in, found {len(extent)} in collection "
            f"<{jsondata['id']}>. See {spec_url} for more info.",
        )
    return True, f"Extent→spatial→bbox for collection is {extent}"


tests_landing: list[Callable[[dict], tuple[bool, str]]] = []
tests_conformance = [requirementA2_2_A5, requirementA11_1]
tests_collection = [requrementA5_2]
