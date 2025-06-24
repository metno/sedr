"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

__license__ = "GPL-2.0"
__version__ = "v0.16.0"

import sys

import pytest

import sedr.edreq12 as edreq
import sedr.metoceanprofilecore10 as metoceanprofilecore
import sedr.metoceanprofileinsituobservations10 as metoceanprofileinsituobservations
import sedr.ogcapi10 as ogcapi
import sedr.preflight
import sedr.util


def run_schemat() -> None:
    sedr.util.logger.info("Running schemathesis tests.")
    # show-capture=no means hide stdout/stderr. Should change debug output instead.
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])


def main() -> None:
    """Run the main program."""

    # Handle --version and --help
    if not sedr.util.args:
        sedr.util.args = sedr.util.parse_args(sys.argv[1:], __version__)
        sedr.util.logger = sedr.util.set_up_logging(
            args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
        )

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
    sedr.util.test_functions["openapi_schema"] = []

    # Check if metocean profile should be auto-included
    if sedr.util.args and not sedr.util.args.metocean_profile_core:
        conformance_is_reachable, conformance_json = sedr.preflight.fetch_conformance(
            url=sedr.util.args.base_url
        )
        if (
            conformance_is_reachable
            and metoceanprofilecore.conformance_url in conformance_json["conformsTo"]
        ):
            sedr.util.logger.info(
                "Enabling tests for MetOcean profile core based on conformance URLs of API."
            )
            sedr.util.args.metocean_profile = True

    if sedr.util.args and sedr.util.args.metocean_profile_core:
        sedr.util.logger.info(
            "Including tests for MetOcean profile core %s",
            metoceanprofilecore.conformance_url,
        )
        sedr.util.test_functions["landing"] += metoceanprofilecore.tests_landing
        sedr.util.test_functions["conformance"] += metoceanprofilecore.tests_conformance
        sedr.util.test_functions["collection"] += metoceanprofilecore.tests_collection
        sedr.util.test_functions["locations_query_response"] = (
            metoceanprofilecore.tests_locations_query_response
        )
        sedr.util.test_functions["openapi_schema"] += (
            metoceanprofilecore.tests_openapi_schema
        )

    if sedr.util.args and sedr.util.args.metocean_profile_insitu_observations:
        sedr.util.logger.info(
            "Including tests for MetOcean profile insitu observations %s",
            metoceanprofileinsituobservations.conformance_url,
        )
        sedr.util.test_functions["collection"] += (
            metoceanprofileinsituobservations.tests_collection
        )

        sedr.util.test_functions["data_query_response"] = (
            metoceanprofileinsituobservations.tests_data_query_response
        )

    if sedr.preflight.main():
        run_schemat()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
