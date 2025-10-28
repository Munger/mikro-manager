#!/usr/bin/env python3
"""
client.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
"""

import librouteros
from librouteros.login import plain, token
from typing import Optional, Dict, List


class MikroTikClient:
    """Wrapper around librouteros for simplified API access"""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 8728, use_ssl: bool = False):
        """
        Initialize MikroTik API client.
        
        Args:
            host: Router hostname or IP
            username: API username
            password: API password
            port: API port (default: 8728, SSL: 8729)
            use_ssl: Use SSL connection
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port if not use_ssl else 8729
        self.use_ssl = use_ssl
        self._api = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def connect(self):
        """Establish connection to router"""
        if self._api:
            return
        
        method = librouteros.connect_ssl if self.use_ssl else librouteros.connect
        
        self._api = method(
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            login_method=plain
        )
    
    def disconnect(self):
        """Close connection to router"""
        if self._api:
            self._api.close()
            self._api = None
    
    @property
    def api(self):
        """Get API connection, connecting if needed"""
        if not self._api:
            self.connect()
        return self._api
    
    def get_path(self, path: str):
        """
        Get API path for executing commands.
        
        Args:
            path: RouterOS API path (e.g., '/ip/dns/static')
            
        Returns:
            API path object
        """
        return self.api.path(path)
