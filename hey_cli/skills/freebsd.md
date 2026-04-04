# FreeBSD Skills
# BSD coreutils, sh/csh default, pkg package manager

- BSD coreutils similar to macOS but not identical.
- `sed -i '' 's/old/new/g'` for in-place sed (same as macOS).
- `xargs -d` NOT supported. Use `tr '\n' '\0' | xargs -0`.
- `grep -P` NOT supported. Use `grep -E`.
- Package manager: `pkg install <pkg>`. Update: `pkg update`. Upgrade: `pkg upgrade`.
- Ports system: `portsnap fetch extract` to sync, then build from `/usr/ports/`.
- Service management via `rc.conf`. Enable: add `<service>_enable="YES"` to `/etc/rc.conf`. Start: `service <service> start`.
- No `systemctl`. Use `service <name> start/stop/restart/status`.
- Default editor is `ee`, not `nano` or `vim`. Install with `pkg install nano`.
- Jails for isolation (similar to containers): `ezjail-admin create`.
- ZFS is native and first-class. Use `zpool` and `zfs` commands.
- Network: `ifconfig` (not `ip`). Route: `route -n get default`.
- Firewall: `pf` (Packet Filter). Config at `/etc/pf.conf`. Enable: `pfctl -e`.
- `stat` uses BSD syntax: `stat -f '%z' <file>` for size.
- Disk operations: `gpart` instead of `fdisk` or `parted`.
