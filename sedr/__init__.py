"""Main init file for sedr. Schemathesis related in schemat.py, others in utils.py."""

import pytest


if __name__ == "__main__":
    pytest.main(["-rA", "--show-capture=no", "./sedr/schemat.py"])
