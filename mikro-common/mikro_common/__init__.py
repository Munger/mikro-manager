#!/usr/bin/env python3
"""
__init__.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
"""

__version__ = "0.1.0"

from .client import MikroTikClient
from .config import load_routers, get_router_config
from .resource import ResourceManager
from .cli import ResourceCLI
from .access import (
    check_permission,
    require_permission,
    load_users,
    load_groups,
    get_user_permissions,
    AccessDeniedError
)

__all__ = [
    "MikroTikClient",
    "load_routers",
    "get_router_config",
    "ResourceManager",
    "ResourceCLI",
    "check_permission",
    "require_permission",
    "load_users",
    "load_groups",
    "get_user_permissions",
    "AccessDeniedError"
]
