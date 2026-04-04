# Windows WSL (Windows Subsystem for Linux) Skills
# GNU coreutils inside WSL, PowerShell outside

- Inside WSL, all standard GNU/Linux commands work (`sed -i`, `grep -P`, `xargs -d`).
- Access Windows drives via `/mnt/c/`, `/mnt/d/`, etc.
- Run Windows executables from WSL: `explorer.exe .`, `notepad.exe <file>`, `cmd.exe /c <command>`.
- Run WSL commands from PowerShell: `wsl <command>`.
- Package manager inside WSL depends on distro (usually `apt` for Ubuntu).
- Service management: WSL2 supports `systemctl` if systemd is enabled in `/etc/wsl.conf`.
- Networking: WSL2 has its own virtual network adapter. Use `ip addr` inside WSL.
- `localhost` access between Windows and WSL2 works automatically.
- Copy between Windows clipboard and WSL: pipe to `clip.exe` or use `powershell.exe Get-Clipboard`.
- File permissions can be odd crossing the `/mnt/` boundary. Use `chmod` carefully.
- Docker Desktop integrates with WSL2 backend. Use `docker` commands directly inside WSL.
- DNS resolution can sometimes break. Fix by editing `/etc/resolv.conf` or configuring `/etc/wsl.conf`.
- `wsl --shutdown` from PowerShell to fully restart WSL.
