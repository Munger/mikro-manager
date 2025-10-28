<!--
README.md : MikroTik management tools

Copyright (c) 2025 Tim Hosking
Website: https://github.com/munger
Licence: MIT
-->

# User Permissions Directory

This directory contains user permission definitions for mikro-manager.

## File Naming Convention

Files are loaded in alphabetical order. Use numeric prefixes to control load order:

- `00-*.yaml` - System defaults (root user)
- `10-*.yaml` - Administrative users
- `20-*.yaml` - Team-specific users
- `30-*.yaml` - Individual users
- `90-*.yaml` - Temporary/guest users

## File Format

```yaml
user:
  username: username
  permissions:
    - groups: [group1, group2]
      routers: "*"        # or [router1, router2]
  comment: "Description"
```

### Access Override

You can override a group's default access level per-user using colon notation:

```yaml
user:
  username: username
  permissions:
    - groups: [group1, "group2:read-only"]
      routers: "*"
  comment: "Has full access to group1, but read-only for group2"
```

## Examples

### Admin User (Full Access)
```yaml
user:
  username: john
  permissions:
    - groups: [full-admin]
      routers: "*"
  comment: "Senior administrator"
```

### DNS Administrator
```yaml
user:
  username: jane
  permissions:
    - groups: [dns-admin]
      routers: "*"
  comment: "DNS management only"
```

### Monitor User (Read-Only)
```yaml
user:
  username: monitor
  permissions:
    - groups: [monitor, "dns-admin:read-only"]
      routers: "*"
  comment: "Monitoring with read-only DNS access"
```

### Multi-Router User
```yaml
user:
  username: bob
  permissions:
    - groups: [dns-admin, dhcp-admin]
      routers: [router1, router2]
  comment: "DNS and DHCP admin for specific routers"
```

## Adding New Users

### Option 1: Grant Full Access (via sudo)
Users with sudo access automatically have full admin rights:
```bash
# No configuration needed - sudo users inherit root permissions
sudo mikro-dns list
```

### Option 2: Grant Limited Access (via mikro-admin group)
For users without sudo who need specific permissions:

1. Create a new file: `sudo nano /etc/mikro-manager/users.d/20-myteam.yaml`
2. Add user definitions
3. Set permissions: `sudo chmod 640 /etc/mikro-manager/users.d/20-myteam.yaml`
4. Add Unix users to mikro-admin group: `sudo usermod -aG mikro-admin username`
5. User logs out and back in for group to take effect

## Security

- All files should be owned by `root:mikro-admin`
- Permissions should be `640` (read-write for root, read for group)
- Only users in the `mikro-admin` group can read these files
