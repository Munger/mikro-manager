#!/usr/bin/env python3
"""
cli.py

  MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
"""

import sys
import argparse
import socket
from mikro_common import MikroTikClient, load_routers, get_router_config, require_permission, AccessDeniedError
from .dns import DNSManager


def cmd_list(args, dns_manager):
    """List all DNS entries"""
    entries = dns_manager.list_entries()
    
    if not entries:
        print("No DNS entries found")
        return
    
    # Print header
    print(f"{'Name':<40} {'Address':<15} {'TTL':<10} {'Comment':<30}")
    print("-" * 100)
    
    # Print entries
    for entry in sorted(entries, key=lambda x: x['name']):
        disabled = " (disabled)" if entry['disabled'] else ""
        comment = entry.get('comment') or ''
        print(f"{entry['name']:<40} {entry['address']:<15} {entry['ttl']:<10} {comment:<30}{disabled}")


def cmd_add(args, dns_manager):
    """Add a new DNS entry"""
    try:
        entry_id = dns_manager.add_entry(
            name=args.name,
            record_type=args.type,
            address=getattr(args, 'address', '') or '',
            cname=getattr(args, 'cname', '') or '',
            mx_preference=getattr(args, 'mx_preference', '') or '',
            mx_exchange=getattr(args, 'mx_exchange', '') or '',
            text=getattr(args, 'text', '') or '',
            ns=getattr(args, 'ns', '') or '',
            srv_priority=getattr(args, 'srv_priority', '') or '',
            srv_weight=getattr(args, 'srv_weight', '') or '',
            srv_port=getattr(args, 'srv_port', '') or '',
            srv_target=getattr(args, 'srv_target', '') or '',
            forward_to=getattr(args, 'forward_to', '') or '',
            regexp=getattr(args, 'regexp', '') or '',
            ttl=args.ttl,
            comment=args.comment
        )
        if args.type == 'CNAME':
            print(f"Added {args.type} record: {args.name} -> {args.cname}")
        elif args.type == 'MX':
            print(f"Added {args.type} record: {args.name} -> {args.mx_exchange}")
        elif args.type == 'NS':
            print(f"Added {args.type} record: {args.name} -> {args.ns}")
        elif args.type == 'SRV':
            print(f"Added {args.type} record: {args.name} -> {args.srv_target}")
        elif args.type in ['TXT', 'NXDOMAIN', 'REGEXP']:
            print(f"Added {args.type} record: {args.name}")
        else:
            print(f"Added {args.type} record: {args.name} -> {args.address}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_update(args, dns_manager):
    """Update an existing DNS entry"""
    updated = dns_manager.update_entry(
        name=args.name,
        record_type=getattr(args, 'type', None),
        address=getattr(args, 'address', None),
        cname=getattr(args, 'cname', None),
        mx_preference=getattr(args, 'mx_preference', None),
        mx_exchange=getattr(args, 'mx_exchange', None),
        text=getattr(args, 'text', None),
        ttl=getattr(args, 'ttl', None),
        comment=getattr(args, 'comment', None)
    )
    
    if updated:
        print(f"Updated DNS entry: {args.name}")
    else:
        print(f"Error: DNS entry '{args.name}' not found", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args, dns_manager):
    """Delete a DNS entry"""
    deleted = dns_manager.delete_entry(args.name)
    
    if deleted:
        print(f"Deleted DNS entry: {args.name}")
    else:
        print(f"Error: DNS entry '{args.name}' not found", file=sys.stderr)
        sys.exit(1)


def cmd_search(args, dns_manager):
    """Search for DNS entries"""
    entries = dns_manager.search_entries(args.pattern)
    
    if not entries:
        print(f"No entries found matching '{args.pattern}'")
        return
    
    print(f"Found {len(entries)} entries matching '{args.pattern}':")
    print(f"{'Name':<40} {'Address':<15} {'TTL':<10} {'Comment':<30}")
    print("-" * 100)
    
    for entry in sorted(entries, key=lambda x: x['name']):
        disabled = " (disabled)" if entry['disabled'] else ""
        comment = entry.get('comment') or ''
        print(f"{entry['name']:<40} {entry['address']:<15} {entry['ttl']:<10} {comment:<30}{disabled}")


def cmd_enable(args, dns_manager):
    """Enable a DNS entry"""
    enabled = dns_manager.enable_entry(args.name)
    
    if enabled:
        print(f"Enabled DNS entry: {args.name}")
    else:
        print(f"Error: DNS entry '{args.name}' not found", file=sys.stderr)
        sys.exit(1)


def cmd_disable(args, dns_manager):
    """Disable a DNS entry"""
    disabled = dns_manager.disable_entry(args.name)
    
    if disabled:
        print(f"Disabled DNS entry: {args.name}")
    else:
        print(f"Error: DNS entry '{args.name}' not found", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args, dns_manager):
    """Validate DNS entries"""
    results = dns_manager.validate_entries()
    
    if not results['duplicates'] and not results['conflicts']:
        print("✓ No issues found")
        return
    
    if results['duplicates']:
        print(f"\n⚠ Found {len(results['duplicates'])} duplicate names:")
        for dup in results['duplicates']:
            print(f"  - {dup['name']}")
    
    if results['conflicts']:
        print(f"\n⚠ Found {len(results['conflicts'])} IP conflicts:")
        for conflict in results['conflicts']:
            print(f"  - {conflict['address']}: {', '.join(conflict['names'])}")


def cmd_export(args, dns_manager):
    """Export DNS entries"""
    output = dns_manager.export_entries(format=args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


def cmd_import(args, dns_manager):
    """Import DNS entries"""
    if args.file:
        with open(args.file, 'r') as f:
            data = f.read()
    else:
        print("Reading from stdin...")
        data = sys.stdin.read()
    
    stats = dns_manager.import_entries(data, format=args.format, overwrite=args.overwrite)
    
    print(f"Import complete:")
    print(f"  Added: {stats['added']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped: {stats['skipped']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage DNS static entries on MikroTik router"
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file'
    )
    parser.add_argument(
        '-r', '--router',
        help='Router name from config (uses default if not specified)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    parser_list = subparsers.add_parser('list', help='List all DNS entries')
    
    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new DNS entry')
    parser_add.add_argument('name', help='DNS name (e.g., server.lan)')
    parser_add.add_argument('--type', default='A', 
                           choices=['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SRV', 'FWD', 'REGEXP', 'NXDOMAIN'], 
                           help='Record type (default: A)')
    parser_add.add_argument('--address', help='IP address (for A/AAAA records)')
    parser_add.add_argument('--cname', help='Target name (for CNAME records)')
    parser_add.add_argument('--mx-preference', help='MX priority (for MX records)')
    parser_add.add_argument('--mx-exchange', help='Mail server (for MX records)')
    parser_add.add_argument('--text', help='Text content (for TXT records)')
    parser_add.add_argument('--ns', help='Name server (for NS records)')
    parser_add.add_argument('--srv-priority', help='SRV priority (for SRV records)')
    parser_add.add_argument('--srv-weight', help='SRV weight (for SRV records)')
    parser_add.add_argument('--srv-port', help='SRV port (for SRV records)')
    parser_add.add_argument('--srv-target', help='SRV target (for SRV records)')
    parser_add.add_argument('--forward-to', help='Forward to server (for FWD records)')
    parser_add.add_argument('--regexp', help='Regular expression (for REGEXP records)')
    parser_add.add_argument('--ttl', default='1d', help='Time to live (default: 1d)')
    parser_add.add_argument('--comment', default='', help='Comment')
    
    # Update command
    parser_update = subparsers.add_parser('update', help='Update an existing DNS entry')
    parser_update.add_argument('name', help='DNS name to update')
    parser_update.add_argument('--type', choices=['A', 'AAAA', 'CNAME', 'MX', 'TXT'], 
                               help='New record type')
    parser_update.add_argument('--address', help='New IP address')
    parser_update.add_argument('--cname', help='New CNAME target')
    parser_update.add_argument('--mx-preference', help='New MX priority')
    parser_update.add_argument('--mx-exchange', help='New mail server')
    parser_update.add_argument('--text', help='New text content')
    parser_update.add_argument('--ttl', help='New TTL')
    parser_update.add_argument('--comment', help='New comment')
    
    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a DNS entry')
    parser_delete.add_argument('name', help='DNS name to delete')
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search for DNS entries')
    parser_search.add_argument('pattern', help='Search pattern (supports wildcards: *, ?)')
    
    # Enable command
    parser_enable = subparsers.add_parser('enable', help='Enable a DNS entry')
    parser_enable.add_argument('name', help='DNS name to enable')
    
    # Disable command
    parser_disable = subparsers.add_parser('disable', help='Disable a DNS entry')
    parser_disable.add_argument('name', help='DNS name to disable')
    
    # Validate command
    parser_validate = subparsers.add_parser('validate', help='Validate DNS entries for conflicts')
    
    # Export command
    parser_export = subparsers.add_parser('export', help='Export DNS entries')
    parser_export.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    parser_export.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    # Import command
    parser_import = subparsers.add_parser('import', help='Import DNS entries')
    parser_import.add_argument('--format', choices=['json', 'csv'], default='json', help='Import format')
    parser_import.add_argument('--file', '-f', help='Input file (default: stdin)')
    parser_import.add_argument('--overwrite', action='store_true', help='Overwrite existing entries')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check permissions before doing anything
    try:
        # Determine required permission based on command
        if args.command in ['list', 'search', 'validate', 'export']:
            require_permission('dns:read')
        else:
            # add, update, delete, enable, disable, import all need write
            require_permission('dns:write')
    except AccessDeniedError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load routers
    try:
        routers = load_routers()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    router_config = get_router_config(routers, args.router)
    
    # Connect to router
    try:
        with MikroTikClient(
            host=router_config['host'],
            username=router_config['username'],
            password=router_config['password'],
            port=router_config.get('port', 8728),
            use_ssl=router_config.get('use_ssl', False)
        ) as client:
            dns_manager = DNSManager(client)
            
            # Execute command
            if args.command == 'list':
                cmd_list(args, dns_manager)
            elif args.command == 'add':
                cmd_add(args, dns_manager)
            elif args.command == 'update':
                cmd_update(args, dns_manager)
            elif args.command == 'delete':
                cmd_delete(args, dns_manager)
            elif args.command == 'search':
                cmd_search(args, dns_manager)
            elif args.command == 'enable':
                cmd_enable(args, dns_manager)
            elif args.command == 'disable':
                cmd_disable(args, dns_manager)
            elif args.command == 'validate':
                cmd_validate(args, dns_manager)
            elif args.command == 'export':
                cmd_export(args, dns_manager)
            elif args.command == 'import':
                cmd_import(args, dns_manager)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
