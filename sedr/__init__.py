"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

import pytest
import util
import schemat


__version__ = "v0.7.4"
edr_version = "1.1"


if __name__ == "__main__":
    # Handle --version and --help
    args = util.parse_args()

    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])
