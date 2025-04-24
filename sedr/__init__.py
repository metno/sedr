"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

__license__ = "GPL-2.0"
__version__ = "v0.10.0"

import sys
import pytest

import util
import preflight
import edreq12 as edreq
import ogcapi10 as ogcapi
import rodeoprofilecore10 as rodeoprofilecore
import rodeoprofileinsituobservations10 as rodeoprofileinsituobservations


def run_schemat() -> None:
    util.logger.info("Running schemathesis tests.")
    # show-capture=no means hide stdout/stderr. Should change debug output instead.
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])


def main() -> None:
    """Run the main program."""

    # Collect tests to run
    util.test_functions["landing"] += edreq.tests_landing + ogcapi.tests_landing
    util.test_functions["conformance"] += (
        edreq.tests_conformance + ogcapi.tests_conformance
    )
    util.test_functions["collection"] += (
        edreq.tests_collection + ogcapi.tests_collections
    )
    util.test_functions["data_query_response"] = []

    if util.args.rodeo_profile_core:
        util.logger.info(
            "Including tests for Rodeo profile core %s",
            rodeoprofilecore.conformance_url,
        )
        util.test_functions["landing"] += rodeoprofilecore.tests_landing
        util.test_functions["conformance"] += rodeoprofilecore.tests_conformance
        util.test_functions["collection"] += rodeoprofilecore.tests_collection

    if util.args.rodeo_profile_insitu_observations:
        util.logger.info(
            "Including tests for Rodeo profile insitu observations %s",
            rodeoprofileinsituobservations.conformance_url,
        )
        util.test_functions["collection"] += (
            rodeoprofileinsituobservations.tests_collection
        )

    # TODO: include profile tests based on conformance_url, https://github.com/metno/sedr/issues/32
    # if rodeoprofile.conformance_url in conformance_json["conformsTo"]:
    #     util.args.rodeo_profile = True

    if preflight.main():
        run_schemat()
    else:
        sys.exit(1)


if __name__ == "__main__":
    # Handle --version and --help
    if not util.args:
        util.args = util.parse_args(sys.argv[1:], __version__)
        util.logger = util.set_up_logging(
            args=util.args, logfile=util.args.log_file, version=__version__
        )

    main()
