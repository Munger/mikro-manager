#!/usr/bin/env python3
"""
test_imports.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
"""

import unittest


class TestImports(unittest.TestCase):
    """Test that all modules can be imported."""

    def test_import_dns(self):
        """Test dns module imports."""
        from mikro_dns import dns
        self.assertTrue(hasattr(dns, 'DNSManager'))

    def test_import_cli(self):
        """Test cli module imports."""
        from mikro_dns import cli
        self.assertTrue(hasattr(cli, 'main'))


if __name__ == '__main__':
    unittest.main()
