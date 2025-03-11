"""rodeo-edr-profile core requirements. See <http://rodeo-project.eu/rodeo-edr-profile>."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import json
import requests
import util

conformance_url = "http://rodeo-project.eu/spec/rodeo-edr-profile/1/req/core"
spec_base_url = (
    "https://rodeo-project.eu/rodeo-edr-profile/standard/rodeo-edr-profile-DRAFT.html"
)


def requirement7_1(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.1. Requirements Class "Core"

    Check if the conformance page contains the required EDR classes.
    jsondata should be a valid conformance page json dict.
    """
    spec_url = f"{spec_base_url}#_requirements_class_core"
    if conformance_url not in jsondata["conformsTo"]:
        return (
            False,
            f"Conformance page /conformance does not contain the profile "
            f"class {conformance_url}. See <{spec_url}> for more info.",
        )
    return True, "Conformance contains conformsTo with required EDR classes."


def requirement7_2(jsondata: dict, timeout: int = 10) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.2. OpenAPI

    jsondata should be a valid landing page json dict.

    returns status: bool, message
    """
    spec_url = f"{spec_base_url}#_openapi"
    openapi_type = "application/vnd.oai.openapi+json;version=3.1"
    servicedoc_type = "text/html"

    service_desc_link = ""
    service_desc_type = ""
    for link in jsondata["links"]:
        if link["rel"] == "service-desc":
            service_desc_link = link["href"]
            service_desc_type = link["type"]
            break

    if not service_desc_link:
        return (
            False,
            f"No service-desc link found. See <{spec_url}> for more info.",
        )

    # C - relation type
    if openapi_type not in service_desc_type:
        return (
            False,
            "OpenAPI link service-desc should identify the content as openAPI "
            f"and include version. Example <{openapi_type}>. Found: "
            f"<{service_desc_type}>. See <{spec_url}> and <{spec_base_url}"
            "#_openapi_2> for more info.",
        )

    # A - described using an OpenAPI document
    response = requests.get(service_desc_link, timeout=timeout)
    if not response.status_code < 400:
        return (
            False,
            f"OpenAPI link service-desc <{service_desc_link}> doesn't respond properly. "
            f"Status code: {response.status_code}.",
        )

    # B - encoded as JSON
    try:
        _ = response.json()
    except (json.JSONDecodeError, TypeError) as err:
        return (
            False,
            f"OpenAPI link service-desc <{service_desc_link}> does not "
            f"contain valid JSON.\nError: {err}",
        )

    # D API documentation
    service_doc_link = ""
    for link in jsondata["links"]:
        if link["rel"] == "service-doc":
            service_doc_link = link["href"]

            if servicedoc_type not in link["type"]:
                return (
                    False,
                    f"Service-doc should have type <{servicedoc_type}>. Found "
                    f"<{link['type']}> See <{spec_url}> for more info.",
                )
            break
    else:
        return (
            False,
            f"Landing page should link to service-doc. See <{spec_url}> for more info.",
        )

    response = requests.get(service_doc_link, timeout=timeout)
    if not response.status_code < 400:
        return (
            False,
            f"OpenAPI link service-desc <{link['href']}> doesn't respond properly. "
            f"Status code: {response.status_code}. See <{spec_url}> for more info.",
        )

    return True, f"{__name__} Landing openapi OK. "


def requirement7_3(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.3. Collection identifier

    Check collection identifier. Can only test B, C.
    Should only be tested if --strict is set.
    """
    spec_url = f"{spec_base_url}#_collection_identifier"
    approved_data_types = [
        "insitu-observations",
        "climate_data",
        "radar_observations",
        "weather_warnings",
        "weather_forecast",
    ]

    # B, C
    try:
        for t in approved_data_types:
            if jsondata["id"].startswith(t):
                break
        else:
            return (
                not util.args.strict,
                f"Collection id SHOULD be from the following list of values: "
                f"{', '.join(approved_data_types)}. A postfix can be added. "
                f"Found: <{jsondata['id']}>. See <{spec_url}> for more info.",
            )
    except (json.JSONDecodeError, KeyError) as err:
        return (
            not util.args.strict,
            f"Collection must have an id. None found in collection <{jsondata}>."
            f"Error {err}.",
        )
    return (
        True,
        "Collection id OK. ",
    )


def requirement7_4(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.4. Collection title

    Check collection title. Can only test A, B.
    """
    spec_url = f"{spec_base_url}#_collection_title"

    # B
    try:
        if len(jsondata["title"]) > 50:
            return (
                False,
                f"Collection title should not exceed 50 chars. See "
                f"<{spec_url}> for more info.",
            )
    except (json.JSONDecodeError, KeyError):
        # A
        return (
            False,
            f"Collection must have a title, but it seems to be missing. See "
            f"<{spec_url}> and {spec_base_url}#_collection_title_2 for more info.",
        )
    return (
        True,
        "Collection title OK. ",
    )


def requirement7_5(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.5. Collection license

    Check collection license. Can't test D.
    """
    spec_url = f"{spec_base_url}#_collection_license"
    wanted_type = "text/html"
    wanted_rel = "license"
    license_count = 0
    # A, B
    for link in jsondata["links"]:
        if link["rel"] == wanted_rel:
            if not link["type"] == wanted_type:
                return (
                    False,
                    f"Collection <{jsondata['id']}> license link should have "
                    f"type='{wanted_type}'. See <{spec_url}> C for more info.",
                )
            license_count += 1

    if license_count > 1:
        return (
            not util.args.strict,
            f"Collection <{jsondata['id']}> has more than one license link.",
        )
    if license_count < 1:
        return (
            False,
            f"Collection <{jsondata['id']}> is missing a license link with "
            f"rel='{wanted_rel}'. See <{spec_url}> A, B for more info.",
        )

    return (
        True,
        "Collection license OK.",
    )

def requirement7_6(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.6. Collection temporal extent

    Check that extent.temporal.trs is set correctly.
    """

    #A
    if jsondata["extent"]["temporal"]["trs"] != "Gregorian":
        return (
            False,
            "Collection temporal extent shall have trs set to 'Gregorian'.",
        )

    return (
        True,
        "Collection temporal extent OK.",
    )

def requirement7_7(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.7. Collection spatial extent

    Check that spatial metadata in collection is set correctly.
    """

    try:
        # A
        if jsondata["extent"]["spatial"]["crs"] != "OGC:CRS84":
            return (
                False,
                "Collection extent.spatial.crs shall be set to 'OGC:CRS84'.",
            )
        # B
        if "OGC:CRS84" not in jsondata["crs"]:
            return (
                False,
                "Collection crs shall include 'OGC:CRS84'.",
            )

        #C
        for q in jsondata["data_queries"]:
            if "crs_details" in q:
                if not any(crs_detail["crs"] == "OGC:CRS84" for crs_detail in q["crs_details"]):
                    return (
                        False,
                        "If crs_details is specified there SHALL be an object with crs set to 'OGC:CRS84'.",
                    )

        #D
        for q in jsondata["data_queries"]:
            if "crs_details" in q and util.args.strict:
                for crs_detail in q["crs_details"]:
                    if crs_detail["crs"] != "OGC:CRS84" and not crs_detail["crs"].startswith("EPSG:"):
                        return (
                            False,
                            "crs in crs_details should be either 'OGC:CRS84' or 'EPSG:<code>'.",
                        )
    except (json.JSONDecodeError, KeyError) as error:
        return (
            False,
            f"Collection spatial metadata is missing required properties: {error}.",
        )

    return (
        True,
        "Collection spatial extent OK.",
    )

def recommendation7_9(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.9. Collection vertical extent

    Check that vertical extent in collection is set correctly.
    """

    allowed_vrs = [
        "Pressure level in hPa",
        "Geopotential height in gpm",
        "Geometrical altitude above mean sea level in meters",
        "Height above ground in meters",
        "Flight level"
    ]

    #A
    if "vertical" in jsondata["extent"] and util.args.strict:
        if jsondata["extent"]["vertical"]["vrs"] not in allowed_vrs:
            return (
                False,
                f"Collection extent.vertical.vrs should be one of the following: {', '.join(allowed_vrs)}.",
            )

    return (
        True,
        "Collection vertical extent OK.",
    )

def requirement7_10(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Core
    Version: 0.1.0
    7.10. Collection parameter names

    Check that collection parameter names are specified correctly.
    """

    #A not tested
    try:
        for p in jsondata["parameter_names"]:
            #B
            if not all(key in p for key in ["label", "description", "unit"]):
                return (
                    False,
                    "Each parameter in parameter_names SHALL include keys 'label', 'description' and 'unit'.",
                )
            #C
            if p["label"].length > 50:
                return (
                    False,
                    "Value for 'label' for an object in 'parameter_names' SHALL not exceed 50 characters.",
                )

            #D no tested

            #E
            if not p["unit"]["symbol"]["type"].startsWith("https://qudt.org/vocab/unit/"):
                return (
                    False,
                    "Value of unit.symbol.type SHALL be on the format 'https://qudt.org/vocab/unit/<unit>'. "
                    "Unit.symbol.value SHALL be set to the value of 'qudt:symbol'.",
                )
            #F
            if util.args.strict and not p["observedProperty"]["id"].startswith("https://vocab.nerc.ac.uk/standard_name/"):
                return (
                    False,
                    "Value of observedProperty SHALL be on the format 'https://vocab.nerc.ac.uk/standard_name/<name>' "
                    "if a suitable CF-convention value exists.",
                )
    except (json.JSONDecodeError, KeyError) as error:
        return (
            False,
            f"Collection parameter_names object is missing required properties: {error}.",
        )

    return (
        True,
        "Collection parameter names OK.",
    )


tests_landing = [requirement7_2]
tests_conformance = [requirement7_1]
tests_collection = [requirement7_3, requirement7_4, requirement7_5, requirement7_6,
                    requirement7_7, recommendation7_9, requirement7_10]