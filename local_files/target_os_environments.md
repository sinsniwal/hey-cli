# Target OS Environments for hey-cli Testing

Based on the 2024 Stack Overflow Developer Survey and real-world command divergence analysis.
Each OS below has meaningfully different shell behavior, coreutils, or package management
that requires dedicated test coverage before production release.

---

## 1. macOS (Darwin)
- **Shell**: zsh (default since Catalina)
- **Coreutils**: BSD — `sed -i ''`, no `xargs -d`, no `grep -P`
- **Package Manager**: `brew`
- **Service Manager**: `launchctl`
- **Key Quirks**: `ifconfig` over `ip`, `dscacheutil` for DNS flush, `open` instead of `xdg-open`, `pbcopy`/`pbpaste` for clipboard

## 2. Ubuntu / Debian
- **Shell**: bash
- **Coreutils**: GNU — full `sed -i`, `xargs -d`, `grep -P`
- **Package Manager**: `apt` / `apt-get`
- **Service Manager**: `systemctl`
- **Key Quirks**: `dpkg` for low-level package ops, `snap` available, `hostname -I` for IP

## 3. Fedora / RHEL / CentOS
- **Shell**: bash
- **Coreutils**: GNU
- **Package Manager**: `dnf` (Fedora), `yum` (RHEL 7/CentOS 7)
- **Service Manager**: `systemctl`
- **Key Quirks**: SELinux enabled by default, `firewall-cmd` instead of `ufw`, `rpm` for low-level packages

## 4. Arch Linux / Manjaro
- **Shell**: bash (zsh popular via oh-my-zsh)
- **Coreutils**: GNU
- **Package Manager**: `pacman` / `yay` (AUR)
- **Service Manager**: `systemctl`
- **Key Quirks**: Rolling release means bleeding-edge binaries, `pacman -Syu` for full upgrade, AUR for community packages

## 5. Windows (PowerShell)
- **Shell**: PowerShell 7 / `cmd.exe`
- **Coreutils**: PowerShell cmdlets — completely different syntax
- **Package Manager**: `winget` / `choco` / `scoop`
- **Service Manager**: `Get-Service` / `sc.exe`
- **Key Quirks**: `Get-ChildItem` not `ls`, `Select-String` not `grep`, backslash `\` paths, `Invoke-WebRequest` not `curl`, `ipconfig` not `ifconfig`

## 6. Windows WSL (Windows Subsystem for Linux)
- **Shell**: bash (runs Ubuntu/Debian/Fedora under Windows)
- **Coreutils**: GNU (inside WSL), PowerShell (outside)
- **Package Manager**: `apt` (if Ubuntu image)
- **Service Manager**: Limited `systemctl` (WSL2 supports systemd)
- **Key Quirks**: `/mnt/c/` to access Windows drives, `wsl.exe` interop, `explorer.exe .` to open Windows Explorer, networking differences from native Linux

## 7. Alpine Linux
- **Shell**: ash (BusyBox)
- **Coreutils**: BusyBox — stripped-down versions of GNU tools
- **Package Manager**: `apk`
- **Service Manager**: `rc-service` / `rc-update` (OpenRC)
- **Key Quirks**: Minimal base (used heavily in Docker), `apk add --no-cache`, no `bash` by default, `musl` libc instead of `glibc`

## 8. FreeBSD
- **Shell**: sh / csh (bash installable)
- **Coreutils**: BSD — similar quirks to macOS but not identical
- **Package Manager**: `pkg`
- **Service Manager**: `service` / `rc.conf`
- **Key Quirks**: `ee` editor instead of `nano`, `portsnap` for ports, jails instead of containers, ZFS native

## 9. openSUSE / SLES
- **Shell**: bash
- **Coreutils**: GNU
- **Package Manager**: `zypper` / `rpm`
- **Service Manager**: `systemctl`
- **Key Quirks**: YaST for system admin, `zypper refresh` instead of `apt update`, Btrfs as default filesystem with snapper snapshots

## 10. ChromeOS (Crostini / Linux container)
- **Shell**: bash (inside Linux container)
- **Coreutils**: GNU (Debian-based container)
- **Package Manager**: `apt` (inside container)
- **Service Manager**: Limited — runs inside a VM
- **Key Quirks**: Must enable Linux Development Environment, limited hardware access, `penguin` container, no direct USB/GPU access without flags

---

## Command Divergence Matrix (Key Areas)

| Area | macOS (BSD) | Linux (GNU) | Windows (PS) | Alpine (BusyBox) |
|------|------------|-------------|--------------|-------------------|
| In-place sed | `sed -i ''` | `sed -i` | N/A | `sed -i` (limited) |
| xargs delimiter | `tr + xargs -0` | `xargs -d` | N/A | `xargs` (no `-d`) |
| Perl regex grep | Not available | `grep -P` | `Select-String` | Not available |
| IP address | `ifconfig` / `ipconfig getifaddr` | `ip addr` / `hostname -I` | `ipconfig` | `ip addr` |
| DNS flush | `dscacheutil -flushcache` | `resolvectl flush-caches` | `ipconfig /flushdns` | N/A |
| Open file/URL | `open` | `xdg-open` | `Start-Process` | N/A |
| Clipboard copy | `pbcopy` | `xclip` / `xsel` | `Set-Clipboard` | N/A |
| Package install | `brew install` | `apt install` | `winget install` | `apk add` |
| Service restart | `launchctl` | `systemctl restart` | `Restart-Service` | `rc-service restart` |
| File manager | `open .` | `nautilus .` / `xdg-open .` | `explorer .` | N/A |
