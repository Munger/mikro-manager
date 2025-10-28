#!/usr/bin/env python3
"""
setup.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
"""

from setuptools import setup, find_packages

setup(
    name="mikro-common",
    version="0.1.0",
    description="Shared library for MikroTik RouterOS API access",
    author="Tim Hosking",
    packages=find_packages(),
    install_requires=[
        "librouteros>=3.1.0",
        "PyYAML>=6.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
