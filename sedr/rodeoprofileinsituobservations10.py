"""rodeo-edr-profile insitu-observations requirements. See <http://rodeo-project.eu/rodeo-edr-profile>."""

__author__ = "MET Norway"
__license__ = "GPL-2.0"

import json
import requests
import util

conformance_url = "http://rodeo-project.eu/spec/rodeo-edr-profile/1/req/insitu-observations"
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
            not util.args.strict,
            f"Collection must have a data_queries object. None found in collection <{jsondata}>."
            f"Error {err}.",
        )
        
    return (
        True,
        "Collection data queries OK. ",
    )

tests_collection = [requirement8_2] 
