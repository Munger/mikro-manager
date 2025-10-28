#!/usr/bin/env python3
"""
cli.py

Base CLI framework for MikroTik resource management tools

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
"""

import sys
import argparse
from typing import Optional, Type
from .client import MikroTikClient
from .resource import ResourceManager
from .config import load_routers, get_router_config
from .access import require_permission, AccessDeniedError


class ResourceCLI:
    """Base class for resource management CLIs"""
    
    # Subclasses should override these
    RESOURCE_NAME = "resource"  # e.g., "dns", "dhcp-server"
    RESOURCE_NAME_PLURAL = "resources"  # e.g., "dns entries", "dhcp servers"
    MANAGER_CLASS: Optional[Type[ResourceManager]] = None
    
    def __init__(self):
        """Initialize CLI"""
        self.parser = None
        self.args = None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create argument parser with common options.
        Subclasses can override to add resource-specific arguments.
        
        Returns:
            ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description=f"Manage {self.RESOURCE_NAME_PLURAL} on MikroTik routers"
        )
        
        # Global options
        parser.add_argument('--router', '-r', help='Router name from config')
        parser.add_argument('--config', '-c', help='Config directory path')
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # List command
        parser_list = subparsers.add_parser('list', help=f'List all {self.RESOURCE_NAME_PLURAL}')
        self.add_list_arguments(parser_list)
        
        # Search command
        parser_search = subparsers.add_parser('search', help=f'Search {self.RESOURCE_NAME_PLURAL}')
        parser_search.add_argument('pattern', help='Search pattern (supports wildcards: *, ?)')
        
        # Enable command
        parser_enable = subparsers.add_parser('enable', help=f'Enable a {self.RESOURCE_NAME}')
        parser_enable.add_argument('identifier', help=f'{self.RESOURCE_NAME.title()} identifier')
        
        # Disable command
        parser_disable = subparsers.add_parser('disable', help=f'Disable a {self.RESOURCE_NAME}')
        parser_disable.add_argument('identifier', help=f'{self.RESOURCE_NAME.title()} identifier')
        
        # Export command
        parser_export = subparsers.add_parser('export', help=f'Export {self.RESOURCE_NAME_PLURAL}')
        parser_export.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
        parser_export.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Import command
        parser_import = subparsers.add_parser('import', help=f'Import {self.RESOURCE_NAME_PLURAL}')
        parser_import.add_argument('--format', choices=['json', 'csv'], default='json', help='Import format')
        parser_import.add_argument('--file', '-f', help='Input file (default: stdin)')
        parser_import.add_argument('--overwrite', action='store_true', help='Overwrite existing entries')
        
        return parser
    
    def add_list_arguments(self, parser: argparse.ArgumentParser):
        """
        Add arguments specific to list command.
        Subclasses can override to add custom list options.
        """
        pass
    
    def add_resource_commands(self, subparsers):
        """
        Add resource-specific commands (add, update, delete, etc.).
        Subclasses should override this to add their specific commands.
        
        Args:
            subparsers: Subparsers object from argparse
        """
        pass
    
    def cmd_list(self, manager: ResourceManager):
        """List all entries"""
        entries = manager.list_entries()
        
        if not entries:
            print(f"No {self.RESOURCE_NAME_PLURAL} found")
            return
        
        self.display_entries(entries)
    
    def display_entries(self, entries):
        """
        Display entries in a formatted way.
        Subclasses should override this for resource-specific formatting.
        
        Args:
            entries: List of entry dictionaries
        """
        # Default: print as simple list
        for entry in entries:
            print(entry)
    
    def cmd_search(self, manager: ResourceManager):
        """Search for entries"""
        entries = manager.search_entries(self.args.pattern)
        
        if not entries:
            print(f"No matching {self.RESOURCE_NAME_PLURAL} found")
            return
        
        print(f"Found {len(entries)} matching {self.RESOURCE_NAME_PLURAL}:")
        self.display_entries(entries)
    
    def cmd_enable(self, manager: ResourceManager):
        """Enable an entry"""
        # Try to find entry by identifier
        entry = self.find_entry_by_identifier(manager, self.args.identifier)
        
        if not entry:
            print(f"Error: {self.RESOURCE_NAME.title()} '{self.args.identifier}' not found", file=sys.stderr)
            sys.exit(1)
        
        manager.enable_entry(entry['.id'])
        print(f"Enabled {self.RESOURCE_NAME}: {self.args.identifier}")
    
    def cmd_disable(self, manager: ResourceManager):
        """Disable an entry"""
        # Try to find entry by identifier
        entry = self.find_entry_by_identifier(manager, self.args.identifier)
        
        if not entry:
            print(f"Error: {self.RESOURCE_NAME.title()} '{self.args.identifier}' not found", file=sys.stderr)
            sys.exit(1)
        
        manager.disable_entry(entry['.id'])
        print(f"Disabled {self.RESOURCE_NAME}: {self.args.identifier}")
    
    def cmd_export(self, manager: ResourceManager):
        """Export entries"""
        output = manager.export_entries(format=self.args.format)
        
        if self.args.output:
            with open(self.args.output, 'w') as f:
                f.write(output)
            print(f"Exported {self.RESOURCE_NAME_PLURAL} to {self.args.output}")
        else:
            print(output)
    
    def cmd_import(self, manager: ResourceManager):
        """Import entries"""
        # Read input
        if self.args.file:
            with open(self.args.file, 'r') as f:
                data = f.read()
        else:
            data = sys.stdin.read()
        
        # Import
        stats = manager.import_entries(
            data,
            format=self.args.format,
            overwrite=self.args.overwrite
        )
        
        print(f"Import complete:")
        print(f"  Added: {stats['added']}")
        print(f"  Updated: {stats['updated']}")
        print(f"  Skipped: {stats['skipped']}")
    
    def find_entry_by_identifier(self, manager: ResourceManager, identifier: str):
        """
        Find an entry by identifier (name, ID, etc.).
        Subclasses should override this for resource-specific lookup.
        
        Args:
            manager: Resource manager instance
            identifier: Entry identifier
            
        Returns:
            Entry dict or None
        """
        # Default: try to find by .id
        entries = manager.list_entries()
        for entry in entries:
            if entry.get('.id') == identifier:
                return entry
        return None
    
    def check_permissions(self):
        """
        Check if user has required permissions.
        Called before executing commands.
        """
        # Determine required permission based on command
        if self.args.command in ['list', 'search', 'export']:
            permission = f'{self.RESOURCE_NAME}:read'
        else:
            permission = f'{self.RESOURCE_NAME}:write'
        
        try:
            require_permission(permission, self.args.config)
        except AccessDeniedError as e:
            print(f"Permission denied: {e}", file=sys.stderr)
            sys.exit(1)
    
    def execute_command(self, manager: ResourceManager):
        """
        Execute the requested command.
        Subclasses can override to handle resource-specific commands.
        
        Args:
            manager: Resource manager instance
        """
        if self.args.command == 'list':
            self.cmd_list(manager)
        elif self.args.command == 'search':
            self.cmd_search(manager)
        elif self.args.command == 'enable':
            self.cmd_enable(manager)
        elif self.args.command == 'disable':
            self.cmd_disable(manager)
        elif self.args.command == 'export':
            self.cmd_export(manager)
        elif self.args.command == 'import':
            self.cmd_import(manager)
        else:
            # Let subclass handle it
            self.execute_resource_command(manager)
    
    def execute_resource_command(self, manager: ResourceManager):
        """
        Execute resource-specific commands.
        Subclasses should override this.
        
        Args:
            manager: Resource manager instance
        """
        print(f"Unknown command: {self.args.command}", file=sys.stderr)
        sys.exit(1)
    
    def run(self):
        """Main entry point for CLI"""
        # Create parser
        self.parser = self.create_parser()
        
        # Add resource-specific commands
        if hasattr(self.parser, '_subparsers'):
            for action in self.parser._subparsers._actions:
                if isinstance(action, argparse._SubParsersAction):
                    self.add_resource_commands(action)
                    break
        
        # Parse arguments
        self.args = self.parser.parse_args()
        
        if not self.args.command:
            self.parser.print_help()
            sys.exit(1)
        
        # Check permissions
        self.check_permissions()
        
        # Load routers
        try:
            routers = load_routers(self.args.config)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        router_config = get_router_config(routers, self.args.router)
        
        # Connect to router and execute command
        try:
            with MikroTikClient(
                host=router_config['host'],
                username=router_config['username'],
                password=router_config['password'],
                port=router_config.get('port', 8728),
                use_ssl=router_config.get('use_ssl', False)
            ) as client:
                # Create manager instance
                if not self.MANAGER_CLASS:
                    raise NotImplementedError("Subclass must set MANAGER_CLASS")
                
                manager = self.MANAGER_CLASS(client)
                
                # Execute command
                self.execute_command(manager)
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
