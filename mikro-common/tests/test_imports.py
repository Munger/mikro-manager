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

    def test_import_config(self):
        """Test config module imports."""
        from mikro_common import config
        self.assertTrue(hasattr(config, 'load_routers'))

    def test_import_access(self):
        """Test access module imports."""
        from mikro_common import access
        self.assertTrue(hasattr(access, 'check_permission'))

    def test_import_client(self):
        """Test client module imports."""
        from mikro_common import client
        self.assertTrue(hasattr(client, 'MikroTikClient'))


if __name__ == '__main__':
    unittest.main()
