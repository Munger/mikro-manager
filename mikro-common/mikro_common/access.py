#!/usr/bin/env python3
"""
access.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
"""

import os
import pwd
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional


CONFIG_DIR = "/etc/mikro-manager"


class AccessDeniedError(PermissionError):
    """Raised when user doesn't have required permissions"""
    pass


def get_current_user() -> str:
    """Get the current Unix username"""
    return pwd.getpwuid(os.getuid()).pw_name


def load_users() -> Dict[str, Dict]:
    """
    Load user configurations from /etc/mikro-manager/users.d directory.
        
    Returns:
        Dictionary mapping usernames to their configurations
    """
    users_dir = os.path.join(CONFIG_DIR, 'users.d')
    
    if not os.path.isdir(users_dir):
        # No users.d directory - allow all access (backward compatibility)
        return {}
    
    users = {}
    yaml_files = sorted(Path(users_dir).glob("*.yaml"))
    
    for yaml_file in yaml_files:
        if yaml_file.name == 'README.md':
            continue
            
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'user' in data:
                    user = data['user']
                    username = user.get('username')
                    if username:
                        users[username] = user
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}")
    
    return users


def load_groups() -> Dict[str, Dict]:
    """
    Load group configurations from /etc/mikro-manager/groups.d directory.
        
    Returns:
        Dictionary mapping group names to their configurations
    """
    groups_dir = os.path.join(CONFIG_DIR, 'groups.d')
    
    if not os.path.isdir(groups_dir):
        return {}
    
    groups = {}
    yaml_files = sorted(Path(groups_dir).glob("*.yaml"))
    
    for yaml_file in yaml_files:
        if yaml_file.name == 'README.md':
            continue
            
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'group' in data:
                    group = data['group']
                    name = group.get('name')
                    if name:
                        groups[name] = group
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}")
    
    return groups


def get_user_permissions(username: str, users: Dict, groups: Dict) -> Set[str]:
    """
    Get all permissions for a user based on their group memberships.
    
    Args:
        username: Username to check
        users: Dictionary of user configurations
        groups: Dictionary of group configurations
        
    Returns:
        Set of permission strings (e.g., 'dns:read', 'dns:write', 'firewall:*')
    """
    # If no users configured, allow all
    if not users:
        return {'*'}
    
    # Check if user exists
    if username not in users:
        return set()
    
    user = users[username]
    permissions_list = user.get('permissions', [])
    
    permissions = set()
    for perm_entry in permissions_list:
        user_groups = perm_entry.get('groups', [])
        
        # Handle multiple formats for groups:
        # Simple: [monitor, dns-admin]
        # With access override: [monitor, "dns-admin:read-only"]
        # Dict format: [{name: dns-admin, access: read-only}]
        for group_item in user_groups:
            # Parse group name and access override
            if isinstance(group_item, dict):
                group_name = group_item.get('name')
                access_override = group_item.get('access')
            elif isinstance(group_item, str) and ':' in group_item:
                # Format: "group-name:access-level"
                group_name, access_override = group_item.split(':', 1)
            else:
                group_name = group_item
                access_override = None
            
            if group_name in groups:
                group = groups[group_name]
                modules = group.get('modules', [])
                # Use override if specified, otherwise use group's access level
                # Support both 'access' and 'default_access' for backward compatibility
                access_level = access_override or group.get('access') or group.get('default_access', 'read-only')
                
                # Handle wildcard modules
                if modules == "*":
                    permissions.add('*')
                    continue
                
                # Ensure modules is a list
                if not isinstance(modules, list):
                    modules = [modules]
                
                # Convert access level to permissions
                for module in modules:
                    if access_level == 'read-write':
                        permissions.add(f"{module}:read")
                        permissions.add(f"{module}:write")
                    elif access_level == 'read-only':
                        permissions.add(f"{module}:read")
                    elif access_level == 'write-only':
                        permissions.add(f"{module}:write")
    
    return permissions


def check_permission(required_permission: str) -> bool:
    """
    Check if current user has the required permission.
    
    Args:
        required_permission: Permission string to check (e.g., 'dns:read', 'dns:write')
        
    Returns:
        True if user has permission, False otherwise
    """
    # Root always has access
    if os.geteuid() == 0:
        return True
    
    username = get_current_user()
    users = load_users()
    groups = load_groups()
    
    # If no users configured, allow all (backward compatibility)
    if not users:
        return True
    
    permissions = get_user_permissions(username, users, groups)
    
    # Check for wildcard permission
    if '*' in permissions:
        return True
    
    # Check for exact match
    if required_permission in permissions:
        return True
    
    # Check for wildcard module permission (e.g., 'dns:*' matches 'dns:read')
    module = required_permission.split(':')[0]
    if f"{module}:*" in permissions:
        return True
    
    return False


def require_permission(required_permission: str):
    """
    Require that current user has the specified permission.
    
    Args:
        required_permission: Permission string to check
        
    Raises:
        AccessDeniedError: If user doesn't have permission
    """
    if not check_permission(required_permission):
        username = get_current_user()
        raise AccessDeniedError(
            f"User '{username}' does not have permission '{required_permission}'"
        )
