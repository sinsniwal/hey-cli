# Arch Linux / Manjaro Skills
# GNU coreutils, bash/zsh, pacman package manager

- In-place sed: `sed -i 's/old/new/g'` (GNU).
- `xargs -d '\n'` and `grep -P` are supported.
- Package manager: `sudo pacman -S <pkg>` to install, `sudo pacman -Syu` for full system upgrade.
- Search packages: `pacman -Ss <query>`. Remove: `sudo pacman -Rns <pkg>`.
- AUR (Arch User Repository): use `yay -S <pkg>` or `paru -S <pkg>` for community packages.
- Service management: `sudo systemctl start/stop/restart/status <service>`.
- Rolling release: packages are always latest version, no version pinning by default.
- Firewall: `sudo ufw` or `iptables` (no default firewall installed).
- Network config: `ip addr`, `nmcli`.
- Open files/URLs: `xdg-open`.
- Clipboard: `xclip` or `xsel`.
- Boot logs: `journalctl -b` for current boot.
- Unlike Debian, there is no `apt`. Never suggest `apt install` on Arch.
- Config files typically live in `/etc/` and are managed manually (no dpkg-reconfigure).
