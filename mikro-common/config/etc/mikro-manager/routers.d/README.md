# Router Configuration Directory

This directory contains router connection definitions for mikro-manager.

## File Naming Convention

Files are loaded in alphabetical order. The **first router** loaded is the default.

- `00-*.yaml` - Primary/default router
- `10-*.yaml` - Secondary routers
- `20-*.yaml` - Remote sites
- `90-*.yaml` - Test/temporary routers

## File Format

```yaml
router:
  name: router-name
  host: hostname.or.ip
  port: 8728
  username: api-user
  password: secure-password
  use_ssl: false
```

## Examples

### Primary Router (Default)
**File: `00-main-router.yaml`**
```yaml
router:
  name: main-router
  host: router.example.com
  port: 8728
  username: api-admin
  password: secure-password
  use_ssl: false
```

### Secondary Router
**File: `10-remote-site.yaml`**
```yaml
router:
  name: remote-site
  host: 192.168.1.1
  port: 8728
  username: admin
  password: another-password
  use_ssl: true
```

## Usage

### Use default router (first file loaded)
```bash
mikro-dns list
```

### Use specific router
```bash
mikro-dns -r remote-site list
```

## Adding New Routers

1. Create a new file: `sudo nano /etc/mikro-manager/routers.d/20-newrouter.yaml`
2. Add router definition
3. Set permissions: `sudo chmod 640 /etc/mikro-manager/routers.d/20-newrouter.yaml`
4. Test connection: `mikro-dns -r newrouter list`

## Security

- All files should be owned by `root:mikro-admin`
- Permissions should be `640` (read-write for root, read for group)
- Contains sensitive credentials - protect carefully
- Only users in the `mikro-admin` group can read these files
