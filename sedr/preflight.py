"""Run a series of simple preflight checks before invoking schemathesis."""

import util
import requests
import json
from urllib.parse import urljoin
import edreq11 as edreq
import rodeoprofile10 as rodeoprofile


def test_site_response(url: str, timeout=10) -> bool:
    """Check basic http response."""
    response = requests.get(url, timeout=timeout)
    if not response.status_code < 400:
        util.logger.error(
            "Landing page doesn't respond correctly: status code: %s",
            response.status_code,
        )
        return False
    return True


def parse_landing(url, timeout=10) -> tuple[bool, dict]:
    """Test that the landing page contains required elements."""
    landing_json = {}
    response = requests.get(url, timeout=timeout)

    try:
        landing_json = response.json()
    except json.decoder.JSONDecodeError:
        util.logger.warning("Landing page <%s> is not valid JSON.", url)
        return False, landing_json

    landing, requirement9_1_message = edreq.requirement9_1(landing_json)
    if not landing:
        util.logger.error(requirement9_1_message)
        return False, landing_json

    requirementA2_2_A7, requirementA2_2_A7_message = edreq.requirementA2_2_A7(
        response.raw.version
    )
    if not requirementA2_2_A7:
        util.logger.error(requirementA2_2_A7_message)
        return False, landing_json

    return True, landing_json


def parse_conformance(url: str, timeout: int, landing_json) -> bool:
    """Test that the conformance page contains required elements."""
    conformance_json = {}
    response = requests.get(url, timeout=timeout)

    try:
        conformance_json = response.json()
    except json.decoder.JSONDecodeError:
        util.logger.warning("Conformance page <%s> is not valid JSON.", url)
        return False

    resolves, resolves_message = util.test_conformance_links(
        jsondata=conformance_json, timeout=util.args.timeout
    )
    if not resolves and util.args.strict:
        util.logger.error(resolves_message)
        if util.args.strict:
            return False

    requirementA2_2_A5, requirementA2_2_A5_message = edreq.requirementA2_2_A5(
        jsondata=conformance_json, siteurl=util.args.url
    )
    if not requirementA2_2_A5:
        util.logger.error(requirementA2_2_A5_message)
        if util.args.strict:
            return False

    requirementA11_1, requirementA11_1_message = edreq.requirementA11_1(
        jsondata=conformance_json
    )
    if not requirementA11_1:
        util.logger.error(requirementA11_1_message)
        if util.args.strict:
            return False

    # Rodeo profile
    if rodeoprofile.conformance_url in conformance_json["conformsTo"]:
        util.args.rodeo_profile = True
    if util.args.rodeo_profile:
        util.logger.info(
            "Including tests for Rodeo profile %s", rodeoprofile.conformance_url
        )

        requirement7_1, requirement7_1_message = rodeoprofile.requirement7_1(
            jsondata=conformance_json
        )
        if not requirement7_1:
            util.logger.error(requirement7_1_message)
            if util.args.strict:
                return False

        requirement7_2, requirement7_2_message = rodeoprofile.requirement7_2(
            jsondata=landing_json, timeout=util.args.timeout
        )
        if not requirement7_2:
            util.logger.error(requirement7_2_message)
            if util.args.strict:
                return False

    return True


def main():
    conformance_url = urljoin(util.args.url, "/conformance")

    if not test_site_response(util.args.url, util.args.timeout):
        return False

    landing_ok, landing_json = parse_landing(util.args.url, util.args.timeout)
    if not landing_ok:
        return False

    if not parse_conformance(conformance_url, util.args.timeout, landing_json):
        return False

    util.logger.info("Preflight checks passed.")
    return True
