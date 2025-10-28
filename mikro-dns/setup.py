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
    name="mikro-dns",
    version="0.1.1",
    description="DNS static entry management for MikroTik routers",
    author="Tim Hosking",
    packages=find_packages(),
    install_requires=[
        "mikro-common>=0.1.0",
    ],
    entry_points={
        'console_scripts': [
            'mikro-dns=mikro_dns.cli:main',
        ],
    },
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
