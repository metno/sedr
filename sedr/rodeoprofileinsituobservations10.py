"""rodeo-edr-profile insitu-observations requirements. See <http://rodeo-project.eu/rodeo-edr-profile>."""

import json

import requests

import sedr.util

conformance_url = (
    "http://rodeo-project.eu/spec/rodeo-edr-profile/1/req/insitu-observations"
)
spec_base_url = (
    "https://rodeo-project.eu/rodeo-edr-profile/standard/rodeo-edr-profile-DRAFT.html"
)


def requirement8_2(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Insitu observations
    Version: 0.1.0
    8.2. Collection data queries

    Check if the collections contains the required data query types.
    """

    required_data_query_types = ["radius", "locations", "area"]
    # A
    try:
        for q in required_data_query_types:
            if q not in jsondata["data_queries"]:
                return (
                    False,
                    f"Collection must have data queries for all required types: "
                    f"{', '.join(required_data_query_types)}. Missing: {q}. "
                    f"Found: {list(jsondata['data_queries'].keys())}. See <{spec_base_url}> for more info.",
                )
    except (json.JSONDecodeError, KeyError) as err:
        return (
            not sedr.util.args.strict,
            f"Collection must have a data_queries object. None found in collection <{jsondata}>."
            f"Error {err}.",
        )

    return (
        True,
        "Collection data queries OK. ",
    )


def requirement8_3(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Insitu observations
    Version: 0.1.0
    8.3. Collection parameter names

    Check if the collections parameter_names are correctly defined.
    """
    try:
        for p in jsondata["parameter_names"]:
            # A, B, C
            if not all(
                key in p
                for key in [
                    "metocean:standard_name",
                    "metocean:level",
                    "measurementType",
                ]
            ):
                return (
                    False,
                    "An object in parameter_names shall have the property 'metocean:standard_name', 'metocean:level' "
                    "and measurementType."
                    f"See <{spec_base_url}> for more info.",
                )
            # C
            cf_cell_methods = [
                "point",
                "sum",
                "maximum",
                "median",
                "mid_range",
                "minimum",
                "mean",
                "mode",
                "range",
                "standard_deviation",
                "variance",
            ]
            if (
                sedr.util.args.strict
                and p["measurementType"]["method"] not in cf_cell_methods
            ):
                return (
                    False,
                    "An object in parameter_names shall have the property 'measurementType' with a 'method' property"
                    f"that is one of the following: {', '.join(cf_cell_methods)}."
                    f"See <{spec_base_url}> for more info.",
                )
    except (json.JSONDecodeError, KeyError) as err:
        return (
            False,
            f"parameter_names has one or more missing properties: {err}.",
        )

    return (
        True,
        "Collection parameter names OK. ",
    )


def requirement8_4(jsondata: dict) -> tuple[bool, str]:
    """
    RODEO EDR Profile Insitu observations
    Version: 0.1.0
    8.4. Collection custom dimensions

    Check if the custom dimensions is correctly defined.
    """
    try:
        # A, C
        if not any(
            custom_dim["id"] == "standard_names"
            and custom_dim["reference"].startswith(
                "https://vocab.nerc.ac.uk/standard_name"
            )
            for custom_dim in jsondata["extent"]["custom"]
        ):
            return (
                False,
                "Collection shall have a custom extent with id 'standard_names' "
                "and reference https://vocab.nerc.ac.uk/standard_name/."
                f"See <{spec_base_url}> for more info.",
            )
        # B not tested
        # D
        if not any(
            custom_dim["id"] == "levels"
            and custom_dim["reference"]
            == "Height of measurement above ground level in meters"
            for custom_dim in jsondata["extent"]["custom"]
        ):
            return (
                False,
                "Collection shall have a custom extent with id 'levels' "
                "and reference 'Height of measurement above ground level in meters'."
                f"See <{spec_base_url}> for more info.",
            )

    except (json.JSONDecodeError, KeyError) as err:
        return (
            False,
            f"extent has one or more missing properties: {err}.",
        )

    return (
        True,
        "Collection custom extent OK. ",
    )


def requirement8_5(resp: requests.Response) -> tuple[bool, str]:
    """
    RODEO EDR Profile Insitu observations
    Version: 0.1.0
    8.5. Data query response format

    Check if the data query response format is correctly defined.
    """
    spec_url = f"{spec_base_url}#_data_query_response_format"

    if resp.headers["Content-Type"] != "application/vnd.cov+json":
        return (
            False,
            "Data query response format SHALL be application/vnd.cov+json. "
            f"Found: {resp.headers['Content-Type']}. See <{spec_url}> for more info.",
        )

    return (
        True,
        "Data query response format OK. ",
    )


def requirement8_6(resp: requests.Response) -> tuple[bool, str]:
    """
    RODEO EDR Profile Insitu observations
    Version: 0.1.0
    8.6. The metadata about parameters in CoverageJSON.


    Check if the parameters in the CoverageJSON data query response is correctly defined.
    """

    spec_url = f"{spec_base_url}#_coveragejson_parameters"

    try:
        for coverage in resp.json()["coverage"]:
            # A
            if not all(
                "metocean:measurementType" in p
                and ["method", "period"] in p["metocean:measurementType"]
                for p in coverage["parameters"]
            ):
                return (
                    False,
                    "CoverageJSON data query response SHALL have a parameters object with metocean:measurementType. "
                    "metocean:measurementType SHALL have method and period properties. "
                    f"See <{spec_url}> for more info.",
                )
            # B
            if not all("metocean:standard_name" in p for p in coverage["parameters"]):
                return (
                    False,
                    "CoverageJSON data query response SHALL have a metocean:standard_name property for all parameters. "
                    f"See <{spec_url}> for more info.",
                )
            # C
            if not all("metocean:level" in p for p in coverage["parameters"]):
                return (
                    False,
                    "CoverageJSON data query response SHALL have a metocean:level property for all parameters. "
                    f"See <{spec_url}> for more info.",
                )

    except (json.JSONDecodeError, KeyError) as err:
        return (
            False,
            f"CoverageJSON data query response has one or more missing properties: {err}.",
        )

    return (
        True,
        "Parameters in CoverageJSON data query response OK. ",
    )


tests_collection = [requirement8_2, requirement8_3, requirement8_4]
tests_data_query_response = [requirement8_5, requirement8_6]
