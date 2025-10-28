<!--
README.md : MikroTik router management tools documentation

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
-->

# Mikro Manager

Suite of tools for managing MikroTik routers via the RouterOS API.

## Modules

- **mikro-common** - Shared library for RouterOS API access
- **mikro-dns** - DNS static entry management
  - List, add, update, delete DNS entries
  - Search with wildcards
  - Enable/disable entries
  - Validate for conflicts
  - Import/export (JSON/CSV)
- **mikro-dhcp** - DHCP lease and static binding management (planned)
- **mikro-firewall** - Firewall rule management (planned)
- **mikro-backup** - Configuration backup and restore (planned)

## Installation

### From Source

```bash
git clone https://github.com/Munger/mikro-manager.git
cd mikro-manager

# Install mikro-common (required)
pip install ./mikro-common

# Install mikro-dns
pip install ./mikro-dns
```

## Development

```bash
cd mikro-manager

# Install in development mode
pip install -e mikro-common/
pip install -e mikro-dns/
```

## License

MIT
