<!--
README.md : MikroTik management tools

Copyright (c) 2025 Tim Hosking
Email: tim@mungerware.com
Website: https://github.com/munger
Licence: MIT
-->

Configuration directory for mikro-manager tools.

## Security Model

### Directory Structure
```
/etc/mikro-manager/
├── routers.d/    # Router connection configs
├── users.d/      # User permission configs
├── groups.d/     # Permission group definitions
└── modules.d/    # Module definitions
```

### Recommended Permissions

**Directories:**
```bash
sudo chown -R root:mikro-admin /etc/mikro-manager
sudo chmod 750 /etc/mikro-manager
sudo chmod 750 /etc/mikro-manager/{routers.d,users.d,groups.d,modules.d}
```

**Files:**
```bash
# Router files - per-user access to protect credentials
sudo chmod 640 /etc/mikro-manager/routers.d/*.yaml
sudo chgrp <username> /etc/mikro-manager/routers.d/<router>.yaml

# User files - each user can only read their own
sudo chmod 640 /etc/mikro-manager/users.d/*.yaml
sudo chgrp <username> /etc/mikro-manager/users.d/<user>.yaml

# Groups and modules - shared by all authorized users
sudo chmod 640 /etc/mikro-manager/groups.d/*.yaml
sudo chmod 640 /etc/mikro-manager/modules.d/*.yaml
sudo chgrp mikro-admin /etc/mikro-manager/{groups.d,modules.d}/*.yaml
```

### User Setup

1. Create mikro-admin group:
```bash
sudo groupadd mikro-admin
```

2. Add authorized users:
```bash
sudo usermod -a -G mikro-admin <username>
```

3. Create user-specific groups for file permissions:
```bash
sudo groupadd <username>  # If not already exists
sudo usermod -a -G <username> <username>
```

### Security Principles

1. **All users must be in mikro-admin group** to use any mikro-* tools
2. **File permissions** prevent users from reading each other's configs
3. **Application logic** (users.d, groups.d) controls what operations are allowed
4. **Only root** can modify configurations
5. **Config directory is hardcoded** to /etc/mikro-manager (cannot be overridden)

This provides defense-in-depth: even if there's a bug in the application, file permissions prevent unauthorized access to credentials and other users' permissions.
