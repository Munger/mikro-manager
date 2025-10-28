<!--
README.md : MikroTik router management tools documentation

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
-->

# Mikro DNS

DNS static entry management for MikroTik routers via the RouterOS API.

## Features

- List all DNS static entries
- Add new DNS entries
- Update existing DNS entries
- Delete DNS entries
- Search entries with wildcards
- Enable/disable entries
- Validate for duplicates and conflicts
- Import/export (JSON/CSV)

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

### Development Installation
```bash
git clone https://github.com/Munger/mikro-manager.git
cd mikro-manager

# Install in development mode
pip install -e mikro-common/
pip install -e mikro-dns/
```

## Configuration

Create `/etc/mikro-manager/routers.d/00-my-router.yaml`:

```yaml
router:
  name: my-router
  host: router.example.com
  port: 8728
  username: api-user
  password: your-password
  use_ssl: false
```

## Usage

### List all DNS entries
```bash
mikro-dns list
```

### Add a DNS entry
```bash
mikro-dns add server.local 192.168.1.100
mikro-dns add server.local 192.168.1.100 --ttl 1h --comment "Production server"
```

### Update a DNS entry
```bash
mikro-dns update server.local --address 192.168.1.101
mikro-dns update server.local --ttl 2d --comment "Updated comment"
```

### Delete a DNS entry
```bash
mikro-dns delete server.local
```

### Search for entries
```bash
# Search by name pattern
mikro-dns search "*.local"
mikro-dns search "server*"

# Search by IP pattern
mikro-dns search "192.168.1.*"
```

### Enable/Disable entries
```bash
# Disable entry without deleting
mikro-dns disable server.local

# Re-enable entry
mikro-dns enable server.local
```

### Validate entries
```bash
# Check for duplicates and conflicts
mikro-dns validate
```

### Export/Import entries
```bash
# Export to JSON
mikro-dns export --format json -o dns-backup.json

# Export to CSV
mikro-dns export --format csv -o dns-backup.csv

# Import from file
mikro-dns import --file dns-backup.json

# Import and overwrite existing entries
mikro-dns import --file dns-backup.json --overwrite

# Import from stdin
cat dns-backup.json | mikro-dns import
```

## License

MIT
