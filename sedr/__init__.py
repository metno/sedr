"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

import pytest
import util


# Handle --version and --help
args = util.parse_args()

pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])
