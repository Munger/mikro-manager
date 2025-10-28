#!/usr/bin/env python3
"""
dns.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
"""

from typing import List, Dict, Optional
from mikro_common import MikroTikClient, ResourceManager


class DNSManager(ResourceManager):
    """Manage DNS static entries on MikroTik router"""
    
    def __init__(self, client: MikroTikClient):
        """
        Initialize DNS manager.
        
        Args:
            client: Connected MikroTikClient instance
        """
        super().__init__(client, '/ip/dns/static')
    
    def list_entries(self) -> List[Dict]:
        """
        List all DNS static entries.
        
        Returns:
            List of dictionaries containing DNS entries
        """
        path = self.client.get_path(self.resource_path)
        entries = []
        
        for entry in path:
            entries.append({
                'id': entry.get('.id'),
                'name': entry.get('name') or '',
                'type': entry.get('type') or 'A',
                'address': entry.get('address') or '',
                'cname': entry.get('cname') or '',
                'mx-preference': entry.get('mx-preference') or '',
                'mx-exchange': entry.get('mx-exchange') or '',
                'text': entry.get('text') or '',
                'ns': entry.get('ns') or '',
                'srv-priority': entry.get('srv-priority') or '',
                'srv-weight': entry.get('srv-weight') or '',
                'srv-port': entry.get('srv-port') or '',
                'srv-target': entry.get('srv-target') or '',
                'forward-to': entry.get('forward-to') or '',
                'regexp': entry.get('regexp') or '',
                'ttl': entry.get('ttl') or '1d',
                'comment': entry.get('comment') or '',
                'disabled': entry.get('disabled', 'false') == 'true'
            })
        
        return entries
    
    def find_entry(self, name: str) -> Optional[Dict]:
        """
        Find DNS entry by name.
        
        Args:
            name: DNS name to search for
            
        Returns:
            Entry dictionary if found, None otherwise
        """
        entries = self.list_entries()
        for entry in entries:
            if entry['name'] == name:
                return entry
        return None
    
    def add_entry(self, name: str, record_type: str = 'A', address: str = '', 
                  cname: str = '', mx_preference: str = '', mx_exchange: str = '',
                  text: str = '', ns: str = '', srv_priority: str = '', 
                  srv_weight: str = '', srv_port: str = '', srv_target: str = '',
                  forward_to: str = '', regexp: str = '', ttl: str = "1d", 
                  comment: str = "", disabled: bool = False) -> str:
        """
        Add a new DNS static entry.
        
        Args:
            name: DNS name (e.g., 'server.lan')
            record_type: Record type (A, AAAA, CNAME, MX, TXT, etc.)
            address: IP address (for A/AAAA records)
            cname: Target name (for CNAME records)
            mx_preference: MX priority (for MX records)
            mx_exchange: Mail server (for MX records)
            text: Text content (for TXT records)
            ns: Name server (for NS records)
            srv_priority: SRV priority (for SRV records)
            srv_weight: SRV weight (for SRV records)
            srv_port: SRV port (for SRV records)
            srv_target: SRV target (for SRV records)
            forward_to: Forward to server (for FWD records)
            regexp: Regular expression (for REGEXP records)
            ttl: Time to live (default: '1d')
            comment: Optional comment
            disabled: Whether entry is disabled
            
        Returns:
            ID of created entry
            
        Raises:
            ValueError: If entry already exists or invalid parameters
        """
        # Check if entry already exists
        existing = self.find_entry(name)
        if existing:
            raise ValueError(f"DNS entry '{name}' already exists. Use update to modify it.")
        
        path = self.client.get_path(self.resource_path)
        
        params = {
            'name': name,
            'type': record_type,
            'ttl': ttl,
        }
        
        # Add type-specific parameters
        if record_type in ['A', 'AAAA']:
            if not address:
                raise ValueError(f"{record_type} record requires an address")
            params['address'] = address
        elif record_type == 'CNAME':
            if not cname:
                raise ValueError("CNAME record requires a cname target")
            params['cname'] = cname
        elif record_type == 'MX':
            if not mx_exchange:
                raise ValueError("MX record requires mx-exchange")
            params['mx-exchange'] = mx_exchange
            if mx_preference:
                params['mx-preference'] = mx_preference
        elif record_type == 'TXT':
            if not text:
                raise ValueError("TXT record requires text content")
            params['text'] = text
        elif record_type == 'NS':
            if not ns:
                raise ValueError("NS record requires a name server")
            params['ns'] = ns
        elif record_type == 'SRV':
            if not srv_target:
                raise ValueError("SRV record requires a target")
            params['srv-target'] = srv_target
            if srv_priority:
                params['srv-priority'] = srv_priority
            if srv_weight:
                params['srv-weight'] = srv_weight
            if srv_port:
                params['srv-port'] = srv_port
        elif record_type == 'FWD':
            if not forward_to:
                raise ValueError("FWD record requires forward-to server")
            params['forward-to'] = forward_to
        elif record_type == 'REGEXP':
            if not regexp:
                raise ValueError("REGEXP record requires a regular expression")
            params['regexp'] = regexp
        elif record_type == 'NXDOMAIN':
            # NXDOMAIN doesn't need additional parameters
            pass
        
        if comment:
            params['comment'] = comment
        
        if disabled:
            params['disabled'] = 'yes'
        
        result = path.add(**params)
        # Result can be a list or a string depending on librouteros version
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('ret', result[0].get('.id', ''))
        return str(result)
    
    def update_entry(self, name: str, record_type: Optional[str] = None,
                    address: Optional[str] = None, cname: Optional[str] = None,
                    mx_preference: Optional[str] = None, mx_exchange: Optional[str] = None,
                    text: Optional[str] = None, ttl: Optional[str] = None, 
                    comment: Optional[str] = None, disabled: Optional[bool] = None) -> bool:
        """
        Update an existing DNS entry.
        
        Args:
            name: DNS name to update
            record_type: New record type (optional)
            address: New IP address (optional)
            cname: New CNAME target (optional)
            mx_preference: New MX priority (optional)
            mx_exchange: New mail server (optional)
            text: New text content (optional)
            ttl: New TTL (optional)
            comment: New comment (optional)
            disabled: New disabled state (optional)
            
        Returns:
            True if updated, False if not found
        """
        entry = self.find_entry(name)
        if not entry:
            return False
        
        path = self.client.get_path(self.resource_path)
        
        params = {'.id': entry['id']}
        
        if record_type is not None:
            params['type'] = record_type
        if address is not None:
            params['address'] = address
        if cname is not None:
            params['cname'] = cname
        if mx_preference is not None:
            params['mx-preference'] = mx_preference
        if mx_exchange is not None:
            params['mx-exchange'] = mx_exchange
        if text is not None:
            params['text'] = text
        if ttl is not None:
            params['ttl'] = ttl
        if comment is not None:
            params['comment'] = comment
        if disabled is not None:
            params['disabled'] = 'yes' if disabled else 'no'
        
        path.update(**params)
        return True
    
    def delete_entry(self, name: str) -> bool:
        """
        Delete a DNS entry by name.
        
        Args:
            name: DNS name to delete
            
        Returns:
            True if deleted, False if not found
        """
        entry = self.find_entry(name)
        if not entry:
            return False
        
        path = self.client.get_path(self.resource_path)
        path.remove(entry['id'])
        return True
    
    def search_entries(self, pattern: str) -> List[Dict]:
        """
        Search for DNS entries matching a pattern.
        
        Args:
            pattern: Search pattern (supports wildcards: *, ?)
            
        Returns:
            List of matching entries
        """
        # Search both name and address fields
        return super().search_entries(pattern, fields=['name', 'address'])
    
    def validate_entries(self) -> Dict[str, List[Dict]]:
        """
        Validate DNS entries for conflicts and issues.
        
        Returns:
            Dictionary with 'duplicates' and 'conflicts' lists
        """
        entries = self.list_entries()
        
        # Check for duplicate names
        name_map = {}
        duplicates = []
        for entry in entries:
            name = entry['name']
            if name in name_map:
                duplicates.append({
                    'name': name,
                    'entries': [name_map[name], entry]
                })
            else:
                name_map[name] = entry
        
        # Check for IP conflicts (same IP, different names)
        ip_map = {}
        conflicts = []
        for entry in entries:
            ip = entry['address']
            if ip in ip_map and ip_map[ip]['name'] != entry['name']:
                conflicts.append({
                    'address': ip,
                    'names': [ip_map[ip]['name'], entry['name']]
                })
            else:
                ip_map[ip] = entry
        
        return {
            'duplicates': duplicates,
            'conflicts': conflicts
        }
    
    # export_entries and import_entries are inherited from ResourceManager
