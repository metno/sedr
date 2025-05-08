"""OGC API Common requirements."""

from collections.abc import Callable
import requests
import sedr.util

ogc_api_common_version = "1.0"
ogc_api_common_url = "https://docs.ogc.org/is/19-072/19-072.html"


def requirement9_1(jsondata: dict) -> tuple[bool, str]:
    """
    OGC API - Common - Part 1: Core
    Version: 1.0.0
    Requirement 9.1

    Test that the landing page contains required elements.

    TODO: See https://github.com/metno/sedr/issues/6 - Should landing page in json only be tested if correct conformance class exists?
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
    return True, "Landing page contains required elements. "


def test_conformance_links(jsondata: dict, timeout: int = 10) -> tuple[bool, str]:
    """
    OGC API - Common - Part 1: Core
    Version: 1.0.0

    Test that all conformance links are valid and resolves. Not belonging to
    any spesific requirement, so not failing unless --strict.
    """
    msg = ""
    valid = True
    for link in jsondata["conformsTo"]:
        if link in [
            "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/conformance",
            "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
            "http://www.opengis.net/spec/ogcapi-edr-1/1.2/req/oas31",
        ]:
            # TODO: These links are part of the standard but doesn't work, so skipping for now.
            msg += f"test_conformance_links Link {link} doesn't resolv, but that is a known issue. "
            continue
        response = requests.Response()
        try:
            response = requests.head(url=link, timeout=timeout)
        except requests.exceptions.MissingSchema as error:
            valid = not sedr.util.args.strict
            msg += f"test_conformance_links Link <{link}> from /conformance is malformed: {error}). "
        if not response.status_code < 400:
            valid = not sedr.util.args.strict
            msg += f"test_conformance_links Link {link} from /conformance is broken (gives status code {response.status_code}). "
    return valid, msg


tests_landing = [requirement9_1]
tests_conformance = [test_conformance_links]
tests_collections: list[Callable[[dict], tuple[bool, str]]] = []
