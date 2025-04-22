"""Unit tests for schemat.py."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import unittest
import util


class TestInit(unittest.TestCase):
    def test_set_up_schemathesis(self):
        """Test set_up_schemathesis."""
        __version__ = "testversion"

        url = "https://edrisobaric.k8s.met.no/"
        util.args = util.parse_args(
            ["--url", url], __version__
        )
        util.args.openapi_version == "3.1"  # pylint:disable=pointless-statement

        landing_page_links = util.fetch_landing_page_links(url)

        util.logger = util.set_up_logging(
            args=util.args, logfile=util.args.log_file, version=__version__
        )
        import schemat  # pylint:disable=import-outside-toplevel

        schemat.schema = schemat.set_up_schemathesis(util.args, landing_page_links)
        self.assertTrue(schemat.schema)
