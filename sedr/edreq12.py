"""EDR requirements."""

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


def requirementA2_2_A5(jsondata: dict, siteurl="") -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.2
    Requirement Annex A2.2 A5

    Check if the conformance page contains the required EDR classes.
    jsondata should be the "conformsTo"-part of the conformance page.
    """
    spec_url = f"{edr_root_url}#req_core_conformance"
    if "conformsTo" not in jsondata:
        return (
            False,
            f"Conformance page <{siteurl}conformance> does not contain a conformsTo attribute. See <{spec_url}> for more info.",
        )
    for url in conformance_urls:
        if url not in jsondata["conformsTo"]:
            return (
                False,
                f"Conformance page <{siteurl}conformance> does not contain the core edr class {url}. See <{spec_url}> for more info.",
            )

    util.logger.debug(
        "requirementA2_2_A5: conformance page contains the required EDR classes."
    )
    return True, ""


def requirementA2_2_A7(version: int) -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.2
    Requirement Annex A2.2 A7

    Check if HTTP1.1 was used.
    """
    spec_url = f"{edr_root_url}#_req_core_http"
    if version == 11:
        util.logger.debug("requirementA2_2_A7 HTTP version 1.1 was used.")
        return True, ""

    return False, f"HTTP version 1.1 was not used. See <{spec_url}> for more info."


def requirementA11_1(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.1
    Requirement A11.1

    Check if the conformance page contains openapi classes, and that they match our version."""
    spec_url = f"{edr_root_url}#_requirements_class_openapi_3_0"

    for url in jsondata["conformsTo"]:
        if url in openapi_conformance_urls:
            if (
                util.args.openapi_version == "3.1"
                and "oas31" in url
                or util.args.openapi_version == "3.0"
                and "oas30" in url
            ):
                util.logger.debug("requirementA11_1 Found openapi class <%s>", url)
                return True, url
            return (
                False,
                f"OpenAPI version {util.args.openapi_version} and version in conformance {url} doesn't match. See <{spec_url}> for more info.",
            )

    return (
        False,
        f"Conformance page /conformance does not contain an openapi class. See <{spec_url}> for more info.",
    )
