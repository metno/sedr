"""OGC API Common requirements."""

import util

ogc_api_common_version = "1.0"
ogc_api_common_url = "https://docs.ogc.org/is/19-072/19-072.html"


def requirement9_1(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Common - Part 1: Core
    Version: 1.0.0
    Requirement 9.1

    Test that the landing page contains required elements.

    TODO: See https://github.com/metno/sedr/issues/6
    """
    spec_ref = f"{ogc_api_common_url}#_7c772474-7037-41c9-88ca-5c7e95235389"

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
