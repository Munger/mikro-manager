#!/usr/bin/env python3
"""
__init__.py

  MikroTik router management tools

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
"""

from .dns import DNSManager

__version__ = "0.1.0"

__all__ = ['DNSManager']
