"""Unit tests for schemat.py."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import unittest
import util


class TestInit(unittest.TestCase):
    def test_set_up_schemathesis(self):
        """Test set_up_schemathesis."""
        __version__ = "testversion"

        util.args = util.parse_args(
            ["--url", "https://edrisobaric.k8s.met.no/"], __version__
        )
        util.args.openapi_version == "3.1"

        util.logger = util.set_up_logging(
            args=util.args, logfile=util.args.log_file, version=__version__
        )
        import schemat

        schemat.schema = schemat.set_up_schemathesis(util.args)
        self.assertTrue(schemat.schema)
