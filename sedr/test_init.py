"""Unit tests for __init__.py."""

__author__ = "Lars Falk-Petersen"
__license__ = "GPL-2.0"

import unittest
import subprocess
import sys


class TestInit(unittest.TestCase):
    def test_version(self):
        result = subprocess.run(
            [sys.executable, "sedr/__init__.py", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("v", result.stdout)

    def test_help(self):
        result = subprocess.run(
            [sys.executable, "sedr/__init__.py", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("usage:", result.stdout)

    def test_run(self):
        result = subprocess.run(
            [
                sys.executable,
                "sedr/__init__.py",
                "--url",
                "https://edrisobaric.k8s.met.no",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
