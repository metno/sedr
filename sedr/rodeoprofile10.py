"""rodeo-edr-profile requirements. See <http://rodeo-project.eu/rodeo-edr-profile>."""

import util

conformance_url = "http://rodeo-project.eu/spec/rodeo-edr-profile/1/req/core"


def requirement7_1(jsondata: str) -> tuple[bool, str]:
    """Check if the conformance page contains the required EDR classes.

    jsondata should be the "conformsTo"-part of the conformance page.
    """
    spec_url = "https://rodeo-project.eu/rodeo-edr-profile/standard/rodeo-edr-profile-DRAFT.html#_requirements_class_core"
    if conformance_url not in jsondata:
        return (
            False,
            f"Conformance page /conformance does not contain the profile class {conformance_url}. See <{spec_url}> for more info.",
        )

    return True, ""

def requirement7_2(jsondata: str) -> tuple[bool, str]:
    """Check OpenAPI."""
    spec_url = "https://rodeo-project.eu/rodeo-edr-profile/standard/rodeo-edr-profile-DRAFT.html#_openapi"
    openapi_type = "application/vnd.oai.openapi+json;version=" #3.0"
    servicedoc_type = "text/html"

    # A, B, C
    for link in jsondata["links"]:
        if link["rel"] == "service-desc":
            if openapi_type not in link["type"]:
                return (
                    False,
                    f"OpenAPI link service-desc should identify the content as openAPI and include version. Example <application/vnd.oai.openapi+json;version=3.0> See <{spec_url}> for more info.",
                )
            break
    else:
        return (
            False,
            f"No service-desc link found. See <{spec_url}> for more info.",
        )

    # D
    for link in jsondata["links"]:
        if link["rel"] == "service-doc":
            if servicedoc_type not in link["type"]:
                return (
                    False,
                    f"Landing page should linkt to service-doc, with type {servicedoc_type}. See <{spec_url}> for more info.",
                )
            break
    else:
        return (
            False,
            f"Landing page should linkt to service-doc, with type {servicedoc_type}. See <{spec_url}> for more info.",
        )