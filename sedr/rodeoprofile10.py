"""rodeo-edr-profile requirements. See <http://rodeo-project.eu/rodeo-edr-profile>."""

import json
import requests
import util

conformance_url = "http://rodeo-project.eu/spec/rodeo-edr-profile/1/req/core"
spec_base_url = (
    "https://rodeo-project.eu/rodeo-edr-profile/standard/rodeo-edr-profile-DRAFT.html"
)


def requirement7_1(jsondata: str) -> tuple[bool, str]:
    """Check if the conformance page contains the required EDR classes."""
    spec_url = f"{spec_base_url}#_requirements_class_core"
    if conformance_url not in jsondata["conformsTo"]:
        return (
            False,
            f"Conformance page /conformance does not contain the profile class {conformance_url}. See <{spec_url}> for more info.",
        )
    util.logger.debug("Rodeoprofile Requirement 7.1 OK")
    return True, ""


def requirement7_2(jsondata: str) -> tuple[bool, str]:
    """
    RODEO EDR Profile
    Version: 0.1.0

    7.2. OpenAPI
    """
    spec_url = f"{spec_base_url}#_openapi"
    openapi_type = "application/vnd.oai.openapi+json;version="  # 3.0"
    servicedoc_type = "text/html"

    for link in jsondata["links"]:
        if link["rel"] == "service-desc":
            # C relation type
            if openapi_type not in link["type"]:
                return (
                    False,
                    f"OpenAPI link service-desc should identify the content as "
                    "openAPI and include version. Example "
                    "<application/vnd.oai.openapi+json;version=3.0>. Found: "
                    f"<{link['type']}> See <{spec_url}> and <{spec_base_url}"
                    "#_openapi_2> for more info.",
                )

            # A described using an OpenAPI document
            response = requests.get(link["href"], timeout=util.args.timeout)
            if not response.status_code < 400:
                return (
                    False,
                    f"OpenAPI link service-desc <{link["href"]}> doesn't respond properly. "
                    f"Status code: {response.status_code}.",
                )

            # B encoded as JSON
            try:
                jsondata = json.loads(response.json())
            except (json.JSONDecodeError, TypeError) as err:
                return (
                    False,
                    f"OpenAPI link service-desc <{link["href"]}> does not contain valid JSON.\n"
                    f"Error: {err}",
                )

    else:
        return (
            False,
            f"No service-desc link found. See <{spec_url}> for more info.",
        )

    # D API documentation
    service_doc_link = ""
    for link in jsondata["links"]:
        if link["rel"] == "service-doc":
            service_doc_link = link["href"]

            if servicedoc_type not in link["type"]:
                return (
                    False,
                    f"Service-doc should have type <{servicedoc_type}>. Found <{link['type']}> See <{spec_url}> for more info.",
                )
            break
    else:
        return (
            False,
            f"Landing page should link to service-doc. See <{spec_url}> for more info.",
        )

    response = requests.get(service_doc_link, timeout=util.args.timeout)
    if not response.status_code < 400:
        return (
            False,
            f"OpenAPI link service-desc <{link["href"]}> doesn't respond properly. "
            f"Status code: {response.status_code}. See <{spec_url}> for more info.",
        )

    util.logger.debug("Rodeoprofile Requirement 7.2 OK")
    return True, ""


def requirement7_3(jsondata) -> tuple[bool, str]:
    """Check collection identifier. Can only test B, C.
    Should only be tested if --strict is set."""
    spec_url = f"{spec_base_url}#_collection_identifier"
    approved_data_types = [
        "insitu-observations",
        "climate_data",
        "radar_observations",
        "weather_warnings",
        "weather_forecast",
    ]

    # B
    try:
        for t in approved_data_types:
            if jsondata["id"].startswith(t):
                break
        else:
            return (
                False,
                f"Collection id SHOULD be from the following list of values: "
                f"{', '.join(approved_data_types)}. A postfix can be added. "
                f"Found: <{jsondata['id']}>. See <{spec_url}> for more info.",
            )
    except (json.JSONDecodeError, KeyError) as err:
        return (
            False,
            f"Collection must have an id. None found in collection <{jsondata}>."
            f"Error {err}.",
        )
    util.logger.debug("Rodeoprofile Requirement 7.3 OK")
    return (
        True,
        "",
    )


def requirement7_4(jsondata: str) -> tuple[bool, str]:
    """Check collection title. Can only test A, B."""
    spec_url = f"{spec_base_url}#_collection_title"

    # B
    try:
        if len(jsondata["title"]) > 50:
            return (
                False,
                f"Collection title should not exceed 50 chars. See <{spec_url}> for more info.",
            )
    except (json.JSONDecodeError, KeyError):
        # A
        return (
            False,
            f"Collection must have a title, but it seems to be missing. See <{spec_url}> and {spec_base_url}#_collection_title_2 for more info.",
        )
    util.logger.debug("Rodeoprofile Requirement 7.4 OK")
    return (
        True,
        "",
    )


def requirement7_5(jsondata: str) -> tuple[bool, str]:
    """Check collection license. Can't test D."""
    spec_url = f"{spec_base_url}#_collection_license"
    # A, B
    for link in jsondata["links"]:
        if link["rel"] == "license":
            if not link["type"] == "text/html":
                return (
                    False,
                    f"Collection <{jsondata['id']}> license link should have type='text/html'. See <{spec_url}> C for more info.",
                )
            break
    else:
        return (
            False,
            f"Collection <{jsondata['id']}> is missing a license link with rel='license'. See <{spec_url}> A, B for more info.",
        )
    util.logger.debug("Rodeoprofile Requirement 7.5 OK")
    return (
        True,
        "",
    )
