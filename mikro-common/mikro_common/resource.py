#!/usr/bin/env python3
"""
resource.py

Base resource manager for MikroTik resources

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
"""

from typing import List, Dict, Optional
from .client import MikroTikClient


class ResourceManager:
    """Base class for managing MikroTik resources"""
    
    def __init__(self, client: MikroTikClient, resource_path: str):
        """
        Initialize resource manager.
        
        Args:
            client: Connected MikroTikClient instance
            resource_path: API path for this resource (e.g., '/ip/dns/static')
        """
        self.client = client
        self.resource_path = resource_path
    
    def list_entries(self) -> List[Dict]:
        """
        List all entries for this resource.
        
        Returns:
            List of dictionaries containing resource entries
        """
        path = self.client.get_path(self.resource_path)
        entries = []
        
        for entry in path:
            entries.append(dict(entry))
        
        return entries
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """
        Get a specific entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Entry dictionary or None if not found
        """
        entries = self.list_entries()
        for entry in entries:
            if entry.get('.id') == entry_id:
                return entry
        return None
    
    def find_entry(self, **kwargs) -> Optional[Dict]:
        """
        Find an entry matching the given criteria.
        
        Args:
            **kwargs: Field values to match
            
        Returns:
            First matching entry or None
        """
        entries = self.list_entries()
        for entry in entries:
            match = all(entry.get(k) == v for k, v in kwargs.items())
            if match:
                return entry
        return None
    
    def add_entry(self, **kwargs) -> str:
        """
        Add a new entry.
        
        Args:
            **kwargs: Entry fields
            
        Returns:
            Entry ID of created entry
        """
        path = self.client.get_path(self.resource_path)
        result = path.add(**kwargs)
        return result
    
    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """
        Update an existing entry.
        
        Args:
            entry_id: Entry ID to update
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        path = self.client.get_path(self.resource_path)
        path.update(**{'.id': entry_id, **kwargs})
        return True
    
    def remove_entry(self, entry_id: str) -> bool:
        """
        Remove an entry.
        
        Args:
            entry_id: Entry ID to remove
            
        Returns:
            True if removed successfully
        """
        path = self.client.get_path(self.resource_path)
        path.remove(entry_id)
        return True
    
    def enable_entry(self, entry_id: str) -> bool:
        """
        Enable a disabled entry.
        
        Args:
            entry_id: Entry ID to enable
            
        Returns:
            True if enabled successfully
        """
        return self.update_entry(entry_id, disabled='false')
    
    def disable_entry(self, entry_id: str) -> bool:
        """
        Disable an entry without deleting it.
        
        Args:
            entry_id: Entry ID to disable
            
        Returns:
            True if disabled successfully
        """
        return self.update_entry(entry_id, disabled='true')
    
    def set_comment(self, entry_id: str, comment: str) -> bool:
        """
        Set comment on an entry.
        
        Args:
            entry_id: Entry ID
            comment: Comment text
            
        Returns:
            True if updated successfully
        """
        return self.update_entry(entry_id, comment=comment)
    
    def search_entries(self, pattern: str, fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for entries matching a pattern.
        
        Args:
            pattern: Search pattern (supports wildcards: *, ?)
            fields: List of field names to search (default: all fields)
            
        Returns:
            List of matching entries
        """
        import fnmatch
        entries = self.list_entries()
        
        if not fields:
            # Search all string fields
            fields = []
            if entries:
                fields = [k for k, v in entries[0].items() if isinstance(v, str)]
        
        matching = []
        for entry in entries:
            for field in fields:
                value = entry.get(field, '')
                if isinstance(value, str) and fnmatch.fnmatch(value, pattern):
                    matching.append(entry)
                    break
        
        return matching
    
    def export_entries(self, format: str = 'json') -> str:
        """
        Export entries to JSON or CSV format.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Formatted string of entries
        """
        entries = self.list_entries()
        
        if format == 'json':
            import json
            return json.dumps(entries, indent=2)
        
        elif format == 'csv':
            import csv
            import io
            output = io.StringIO()
            if entries:
                writer = csv.DictWriter(output, fieldnames=entries[0].keys())
                writer.writeheader()
                writer.writerows(entries)
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_entries(self, data: str, format: str = 'json', 
                      overwrite: bool = False, key_field: str = 'name') -> Dict[str, int]:
        """
        Import entries from JSON or CSV format.
        
        Args:
            data: Data string to import
            format: Import format ('json' or 'csv')
            overwrite: Whether to overwrite existing entries
            key_field: Field name to use for matching existing entries
            
        Returns:
            Dictionary with counts: {'added': N, 'updated': N, 'skipped': N}
        """
        import json
        import csv
        import io
        
        # Parse data
        if format == 'json':
            entries = json.loads(data)
        elif format == 'csv':
            reader = csv.DictReader(io.StringIO(data))
            entries = list(reader)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        stats = {'added': 0, 'updated': 0, 'skipped': 0}
        
        for entry in entries:
            # Remove internal fields
            entry.pop('.id', None)
            
            # Check if entry exists
            key_value = entry.get(key_field)
            if not key_value:
                stats['skipped'] += 1
                continue
            
            existing = self.find_entry(**{key_field: key_value})
            
            if existing:
                if overwrite:
                    self.update_entry(existing['.id'], **entry)
                    stats['updated'] += 1
                else:
                    stats['skipped'] += 1
            else:
                self.add_entry(**entry)
                stats['added'] += 1
        
        return stats
