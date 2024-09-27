"""EDR requirements."""

import sedr.util as util

conformance_urls = [
    "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/core",
    "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
    "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/core",
]
openapi_conformance_urls = [
    "http://www.opengis.net/spec/ogcapi-edr-1/1.1/req/oas30",
    "http://www.opengis.net/spec/ogcapi-edr-1/1.2/req/oas31",
]


def requirementA2_2_A5(jsondata: str) -> tuple[bool, str]:
    """Check if the conformance page contains the required EDR classes.

    jsondata should be the "conformsTo"-part of the conformance page.
    """
    spec_url = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_c9401fee-54b9-d116-8365-af0f85a8243d"
    for url in conformance_urls:
        if url not in jsondata:
            return (
                False,
                f"Conformance page /conformance does not contain the core edr class {url}. See <{spec_url}> for more info.",
            )

    return True, ""


def requirementA2_2_A7(version: int) -> tuple[bool, str]:
    """Check if HTTP1.1 was used."""
    spec_url = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_0d0c25a0-850f-2aa5-9acb-06efcc04d452"
    if version == 11:
        return True, ""

    return False, f"HTTP version 1.1 was not used. See <{spec_url}> for more info."


def requirementA11_1(jsondata: str) -> tuple[bool, str]:
    """Check if the conformance page contains openapi classes, and that they match our version."""
    spec_url = "https://docs.ogc.org/is/19-086r6/19-086r6.html#_cc7dd5e3-1d54-41ff-b5ba-c5fcb99fa663"

    for url in jsondata:
        if url in openapi_conformance_urls:
            if util.args and (
                util.args.openapi_version == "3.1"
                and "oas31" in url
                or util.args.openapi_version == "3.0"
                and "oas30" in url
            ):
                return True, url
            return (
                False,
                f"OpenAPI version {util.args.openapi_version if util.args else "unknown"} and version in conformance {url} doesn't match. See <{spec_url}> for more info.",
            )

    return (
        False,
        f"Conformance page /conformance does not contain an openapi class. See <{spec_url}> for more info.",
    )
