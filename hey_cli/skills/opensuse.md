# openSUSE / SLES Skills
# GNU coreutils, bash default, zypper package manager

- In-place sed: `sed -i 's/old/new/g'` (GNU).
- `xargs -d '\n'` and `grep -P` are supported.
- Package manager: `sudo zypper install <pkg>`. Refresh repos: `sudo zypper refresh`. Update: `sudo zypper update`.
- Search: `zypper search <query>`. Remove: `sudo zypper remove <pkg>`.
- Low-level packages: `rpm -ivh <file>.rpm`.
- YaST system administration tool: `sudo yast` (TUI) or `sudo yast2` (GUI).
- Service management: `sudo systemctl start/stop/restart/status <service>`.
- Default filesystem is Btrfs with automatic snapshots via `snapper`.
- Rollback snapshots: `sudo snapper list`, `sudo snapper rollback <id>`.
- Firewall: `sudo firewall-cmd` (firewalld) same as Fedora/RHEL.
- Network config: `ip addr`, `nmcli`, or via YaST.
- Open files/URLs: `xdg-open`.
- Clipboard: `xclip` or `xsel`.
- Tumbleweed (rolling) vs Leap (stable) — package availability may differ.
