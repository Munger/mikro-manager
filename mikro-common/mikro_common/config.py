#!/usr/bin/env python3
"""
config.py

  MikroTik router management tools

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional


CONFIG_DIR = "/etc/mikro-manager"


def load_routers() -> Dict[str, Dict]:
    """
    Load router configurations from /etc/mikro-manager/routers.d directory.
    
    Returns:
        Dictionary mapping router names to their configurations
        
    Raises:
        FileNotFoundError: If no router directory found
        PermissionError: If config directory has incorrect permissions
    """
    router_dir = os.path.join(CONFIG_DIR, 'routers.d')
    
    if not os.path.isdir(router_dir):
        raise FileNotFoundError(
            f"Router directory not found: {router_dir}\n"
            f"Create router configs in /etc/mikro-manager/routers.d/"
        )
    
    # Security checks (skip if running as root)
    if os.geteuid() != 0:
        # Verify directory is owned by root
        dir_stat = os.stat(router_dir)
        if dir_stat.st_uid != 0:
            raise PermissionError(
                f"Security error: {router_dir} must be owned by root. "
                f"Current owner UID: {dir_stat.st_uid}"
            )
    
    # Load all .yaml files in alphabetical order
    routers = {}
    yaml_files = sorted(Path(router_dir).glob("*.yaml"))
    
    for yaml_file in yaml_files:
        if yaml_file.name == 'README.md':
            continue
        
        # Verify file is owned by root (security check)
        if os.geteuid() != 0:
            file_stat = os.stat(yaml_file)
            if file_stat.st_uid != 0:
                print(f"Warning: Skipping {yaml_file} - not owned by root (UID: {file_stat.st_uid})")
                continue
            
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'router' in data:
                    router = data['router']
                    name = router.get('name')
                    if name:
                        routers[name] = router
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}")
    
    if not routers:
        raise FileNotFoundError(f"No valid router configurations found in {router_dir}")
    
    return routers


def get_router_config(routers: Dict[str, Dict], router_name: Optional[str] = None) -> Dict:
    """
    Get router connection settings.
    
    Args:
        routers: Dictionary of router configurations
        router_name: Name of router to use (optional, uses first if not specified)
        
    Returns:
        Router configuration dictionary
        
    Raises:
        ValueError: If router not found
    """
    if not routers:
        raise ValueError("No routers configured")
    
    # Use specified router
    if router_name:
        if router_name not in routers:
            raise ValueError(f"Router '{router_name}' not found. Available: {', '.join(routers.keys())}")
        return routers[router_name]
    
    # Use first router (default)
    return list(routers.values())[0]
