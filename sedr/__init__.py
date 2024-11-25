"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-3.0"
__version__ = "v0.8.0"

import sys
import pytest
import util
import preflight


def run_schemat() -> None:
    # show-capture=no means hide stdout/stderr. Should change debug output instead.
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])


def main() -> None:
    """Run the main program."""
    if preflight.main():
        run_schemat()
    else:
        sys.exit(1)


# Handle --version and --help
util.args = util.parse_args(sys.argv[1:], __version__)
util.logger = util.set_up_logging(
    args=util.args, logfile=util.args.log_file, version=__version__
)
main()
