"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

import pytest
import util
import schemat


__author__ = "Lars Falk-Petersen"
__version__ = "v0.7.4"
__license__ = "GPL-3.0"
edr_version = "1.1"


if __name__ == "__main__":
    # Handle --version and --help
    args = util.parse_args()

    # show-capture=no means hide stdout/stderr. Should change debug output instead.
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])
