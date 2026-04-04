# Ubuntu / Debian Skills
# GNU coreutils, bash default, apt package manager

- In-place sed: `sed -i 's/old/new/g'` (no extension argument needed).
- `xargs -d '\n'` is supported for newline delimiters.
- `grep -P` (Perl regex) is supported.
- Local IP: `hostname -I` or `ip addr show`.
- DNS flush: `sudo resolvectl flush-caches` or `sudo systemd-resolve --flush-caches`.
- Open files/URLs with `xdg-open`.
- Clipboard: use `xclip -selection clipboard` or `xsel --clipboard`.
- Package manager is `apt`. Install with `sudo apt install <pkg>`. Always `sudo apt update` first.
- Service management: `sudo systemctl start/stop/restart/status <service>`.
- `readlink -f` is supported natively.
- `date -d @<epoch>` for epoch conversion.
- `stat -c '%s' <file>` for file size.
- Low-level packages: `dpkg -i <file>.deb`, `dpkg -l` to list.
- Firewall: `sudo ufw enable/disable/status`, `sudo ufw allow <port>`.
- `snap` is available for sandboxed packages.
- Network config: `ip addr`, `ip route`, `ip link`.
- Process on port: `sudo lsof -i :<port>` or `sudo ss -tlnp | grep <port>`.
