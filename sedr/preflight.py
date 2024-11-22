""" Run a series of simple preflight checks before invoking schemathesis. """

import sys
import util
import requests
import edreq11 as edreq
import rodeoprofile10 as rodeoprofile


def test_site_response(url: str, timeout=10) -> bool:
    """Check basic response."""
    response = requests.get(util.args.url, timeout=timeout)
    if not response.status_code < 400:
        util.logger.error(f"Landing page doesn't respond correctly: status code: {response.status_code}")
        return False
    return True


def parse_landingpage(url, timeout=10) -> bool:
    """Test that the landing page contains required elements."""
    landingpage_json = None
    response = requests.get(util.args.url, timeout=timeout)

    try:
        landingpage_json = response.json()
    except json.decoder.JSONDecodeError:
        util.logger.warning("Landing page is not valid JSON.")
        return False

    landing, requirement9_1_message = edreq.requirement9_1(landingpage_json)
    if not landing:
        util.logger.error(requirement9_1_message)
        return False

    if util.args.rodeo_profile:
        requirement7_2, requirement7_2_message = rodeoprofile.requirement7_2(
            jsondata=landingpage_json
        )
        if not requirement7_2:
            util.logger.error(requirement7_2_message)
            return False
    return True


def main():
    if test_site_response(util.args.url, util.args.timeout) and \
        parse_landingpage(util.args.url, util.args.timeout):
        return True
    return False
