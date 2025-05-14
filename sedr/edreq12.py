"""EDR requirements."""

from collections.abc import Callable

import sedr.util

edr_version = "1.2"
edr_root_url = "https://docs.ogc.org/DRAFTS/19-086r7.html"
ogc_api_common_url = "https://docs.ogc.org/is/19-072/19-072.html"
conformance_urls = [
    "https://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
    "https://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
    "https://www.opengis.net/spec/ogcapi-edr-1/1.2/conf/core",
]
openapi_conformance_urls = [
    "https://www.opengis.net/spec/ogcapi-edr-1/1.2/req/oas31",
]


def requirementA2_2_A3(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.2
    Requirement Annex A2.2 A3

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
        if url.split("://", 1)[-1] not in (
            u.split("://", 1)[-1] for u in jsondata["conformsTo"]
        ):
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
    spec_url = f"{edr_root_url}#_requirements_class_openapi_specification_3_1"

    for url in jsondata["conformsTo"]:
        if url.split("://", 1)[-1] in (
            u.split("://", 1)[-1] for u in openapi_conformance_urls
        ):
            if "oas31" in url:
                return True, f"Found openapi class <{url}>. "
            return (
                False,
                f"OpenAPI version {sedr.util.args.openapi_version} and version in "
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

    try:
        extent = sedr.util.parse_spatial_bbox(jsondata)
    except Exception as err:
        return (
            False,
            f"Extent in collection <{jsondata['id']}> is not valid: {err}. See {spec_url} for more info.",
        )
    return True, f"Extent→spatial→bbox for collection is {extent}"


tests_landing: list[Callable[[dict], tuple[bool, str]]] = []
tests_conformance = [requirementA2_2_A3, requirementA11_1]
tests_collection = [requrementA5_2]
