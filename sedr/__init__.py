"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-3.0"
__version__ = "v0.7.5"

import pytest
import util


def main():
    # show-capture=no means hide stdout/stderr. Should change debug output instead.
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])
    # pytest.main(["-rA", "./sedr/schemat.py"])


# Handle --version and --help
util.args = util.parse_args(__version__)
util.logger = util.set_up_logging(
    args=util.args, logfile=util.args.log_file, version=__version__
)
main()
