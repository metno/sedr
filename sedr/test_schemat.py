"""Unit tests for schemat.py."""

import unittest

import sedr.util


class TestInit(unittest.TestCase):
    def test_set_up_schemathesis(self):
        """Test set_up_schemathesis."""
        __version__ = "testversion"

        url = "https://edrisobaric.k8s.met.no/"
        sedr.util.args = sedr.util.parse_args(["--url", url], __version__)
        sedr.util.args.openapi_version == "3.1"  # noqa: B015 # pylint: disable=pointless-statement

        landing_page_links = sedr.util.fetch_landing_page_links(url)

        sedr.util.logger = sedr.util.set_up_logging(
            args=sedr.util.args, logfile=sedr.util.args.log_file, version=__version__
        )
        import schemat  # pylint:disable=import-outside-toplevel

        schemat.schema = schemat.set_up_schemathesis(sedr.util.args, landing_page_links)
        self.assertTrue(schemat.schema)
