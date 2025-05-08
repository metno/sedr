"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

__license__ = "GPL-2.0"
__version__ = "v0.11.0"

import sys
import pytest

import sedr.util
import sedr.preflight
import sedr.edreq12 as edreq
import sedr.ogcapi10 as ogcapi
import sedr.rodeoprofilecore10 as rodeoprofilecore
import sedr.rodeoprofileinsituobservations10 as rodeoprofileinsituobservations


def run_schemat() -> None:
    sedr.util.logger.info("Running schemathesis tests.")
    # show-capture=no means hide stdout/stderr. Should change debug output instead.
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])


def main() -> None:
    """Run the main program."""

    # Collect tests to run
    sedr.util.test_functions["landing"] += edreq.tests_landing + ogcapi.tests_landing
    sedr.util.test_functions["conformance"] += (
        edreq.tests_conformance + ogcapi.tests_conformance
    )
    sedr.util.test_functions["collection"] += (
        edreq.tests_collection + ogcapi.tests_collections
    )
    sedr.util.test_functions["data_query_response"] = []
    sedr.util.test_functions["locations_query_response"] = []

    if sedr.util.args.rodeo_profile_core:
        sedr.util.logger.info(
            "Including tests for Rodeo profile core %s",
            rodeoprofilecore.conformance_url,
        )
        sedr.util.test_functions["landing"] += rodeoprofilecore.tests_landing
        sedr.util.test_functions["conformance"] += rodeoprofilecore.tests_conformance
        sedr.util.test_functions["collection"] += rodeoprofilecore.tests_collection
        sedr.util.test_functions["locations_query_response"] = (
            rodeoprofilecore.tests_locations_query_response
        )

    if sedr.util.args.rodeo_profile_insitu_observations:
        sedr.util.logger.info(
            "Including tests for Rodeo profile insitu observations %s",
            rodeoprofileinsituobservations.conformance_url,
        )
        sedr.util.test_functions["collection"] += (
            rodeoprofileinsituobservations.tests_collection
        )

    # TODO: include profile tests based on conformance_url, https://github.com/metno/sedr/issues/32
    # if rodeoprofile.conformance_url in conformance_json["conformsTo"]:
    #     sedr.util.args.rodeo_profile = True

    if sedr.preflight.main():
        run_schemat()
    else:
        sys.exit(1)


if __name__ == "__main__":
    # Handle --version and --help
    if not sedr.util.args:
        sedr.util.args = sedr.util.parse_args(sys.argv[1:], __version__)
        sedr.util.logger = sedr.util.set_up_logging(
            args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
        )

    main()
