"""Run a series of simple preflight checks before invoking schemathesis."""

import util
import requests
import json


def fetch_landing(url: str, timeout: int) -> tuple[bool, dict]:
    """Test that the landing page contains required elements."""
    landing_json = {}
    response = requests.Response()

    try:
        response = requests.get(url, timeout=timeout)
        landing_json = response.json()
    except requests.exceptions.ConnectionError as err:
        util.logger.error(
            f"Unable to get landing page <%s>.\n%s", url, err
        )
        return False, landing_json
    except json.decoder.JSONDecodeError as err:
        util.logger.error(
            f"fetch_landing Landing page <%s> is not valid JSON.\n%s", url, err
        )
        return False, landing_json
    return True, landing_json


def fetch_conformance(url: str, timeout: int) -> tuple[bool, dict]:
    """Test that the conformance page contains required elements."""
    conformance_url = util.build_conformance_url(url)
    conformance_json = {}
    response = requests.Response()

    try:
        response = requests.get(conformance_url, timeout=timeout)
        conformance_json = response.json()
    except requests.exceptions.ConnectionError as err:
        util.logger.error(
            f"Unable to get conformance <%s>.\n%s", url, err
        )
        return False, conformance_json
    except json.decoder.JSONDecodeError as err:
        util.logger.error(
            "Conformance <%s> is not valid JSON:\n%s", conformance_url, err
        )
        return False, conformance_json
    return True, conformance_json


def main():
    # Get landing
    landing_is_reachable, landing_json = fetch_landing(util.args.url, util.args.timeout)
    if not landing_is_reachable:
        return False

    # Run tests for landing
    for f in util.test_functions["landing"]:
        status, msg = f(landing_json)
        if not status:
            util.logger.error("Test %s failed with message: %s", f.__name__, msg)
        else:
            util.logger.info("Test %s passed. (%s)", f.__name__, msg)

    # Get conformance
    conformance_is_reachable, conformance_json = fetch_conformance(
        util.args.url, util.args.timeout
    )
    if not conformance_is_reachable:
        return False

    # Run tests for conformance page
    for f in util.test_functions["conformance"]:
        status, msg = f(conformance_json)
        if not status:
            util.logger.error("Test %s failed with message: %s", f.__name__, msg)
        else:
            util.logger.debug("Test %s passed. (%s)", f.__name__, msg)

    util.logger.info("Preflight checks done.")
    return True


if __name__ == "__main__":
    main()
