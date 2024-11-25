"""EDR requirements."""

import util

__edr_version__ = "1.1"
conformance_urls = [
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
    f"http://www.opengis.net/spec/ogcapi-edr-1/{__edr_version__}/conf/core",
]
openapi_conformance_urls = [
    "http://www.opengis.net/spec/ogcapi-edr-1/1.1/req/oas30",
    "http://www.opengis.net/spec/ogcapi-edr-1/1.2/req/oas31",
]


def requirementA2_2_A5(jsondata: dict, siteurl="") -> tuple[bool, str]:
    """
    OGC API - Environmental Data Retrieval Standard
    Version: 1.1
    Requirement Annex A2.2 A5

    Check if the conformance page contains the required EDR classes.
    jsondata should be the "conformsTo"-part of the conformance page.
    """
    spec_url = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_c9401fee-54b9-d116-8365-af0f85a8243d"
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
    Version: 1.1
    Requirement Annex A2.2 A7

    Check if HTTP1.1 was used.
    """
    spec_url = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_0d0c25a0-850f-2aa5-9acb-06efcc04d452"
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
    spec_url = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_cc7dd5e3-1d54-41ff-b5ba-c5fcb99fa663"

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


def requirement9_1(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Common - Part 1: Core
    Version: 1.0.0
    Requirement 9.1

    Test that the landing page contains required elements.

    TODO: See https://github.com/metno/sedr/issues/6
    """
    spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_7c772474-7037-41c9-88ca-5c7e95235389"

    if "title" not in jsondata:
        return (
            False,
            "Landing page does not contain a title. See <{spec_ref}> for more info.",
        )
    if "description" not in jsondata:
        return (
            False,
            "Landing page does not contain a description. See <{spec_ref}> for more info.",
        )
    if "links" not in jsondata:
        return (
            False,
            "Landing page does not contain links. See <{spec_ref}> for more info.",
        )

    service_desc = ""
    for link in jsondata["links"]:
        if not isinstance(link, dict):
            return (
                False,
                f"Link {link} is not a dictionary. See <{spec_ref}> for more info.",
            )
        if "href" not in link:
            return (
                False,
                f"Link {link} does not have a href attribute. See <{spec_ref}> for more info.",
            )
        if "rel" not in link:
            return (
                False,
                f"Link {link} does not have a rel attribute. See <{spec_ref}> for more info.",
            )
        if link["rel"] == "service-desc":
            service_desc = link["href"]
    if not service_desc:
        return (
            False,
            f"Landing page does not contain a service-desc link. See <{spec_ref}> for more info.",
        )
    util.logger.debug("requirement9_1 Landing page contains required elements.")
    return True, ""
