"""Unit tests for schemat.py."""

import unittest
import util


class TestInit(unittest.TestCase):
    def test_set_up_schemathesis(self):
        """Test set_up_schemathesis."""
        __version__ = "testversion"

        util.args = util.parse_args([], __version__)
        util.args.openapi_version == "3.1"

        util.logger = util.set_up_logging(
           args=util.args, logfile=util.args.log_file, version=__version__
        )
        import schemat

        schemat.schema = schemat.set_up_schemathesis(util.args)
        self.assertTrue(schemat.schema)


    # def test_edr_landingpage(self):
    #     """Test test_edr_landingpage."""
    #     __version__ = "testversion"

    #     util.args = util.parse_args([], __version__)
    #     util.args.openapi_version == "3.1"

    #     util.logger = util.set_up_logging(
    #        args=util.args, logfile=util.args.log_file, version=__version__
    #     )
    #     import schemat

    #     schemat.schema = schemat.set_up_schemathesis(util.args)

    # TODO: Need to set up a case to run this
    #     t = schemat.test_edr_landingpage()
    #     self.assertTrue(t)
