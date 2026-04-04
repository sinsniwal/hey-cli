# ChromeOS (Crostini / Linux Container) Skills
# Debian-based GNU coreutils inside Linux container

- Linux must be enabled first: Settings > Advanced > Developers > Linux Development Environment.
- Container name is `penguin` by default.
- Package manager: `sudo apt update && sudo apt install <pkg>` (Debian-based).
- Inside the container, standard GNU commands work: `sed -i`, `grep -P`, `xargs -d`.
- Limited hardware access: USB devices need explicit sharing, GPU acceleration requires flags.
- No direct `systemctl` — container runs under LXC, not full systemd.
- File sharing: Linux files at `/home/<user>/`, shared with ChromeOS Files app under "Linux files".
- Access Android/ChromeOS downloads: shared folders appear under `/mnt/chromeos/`.
- No native Docker support in Crostini (nested virtualization limited). Use Podman instead.
- `xdg-open` may work for opening files in ChromeOS apps.
- Audio/video support may be limited depending on ChromeOS version.
- Network uses Chrome's network stack. Ports opened in container are accessible from ChromeOS browser.
- Backup: `lxc export penguin backup.tar.gz` or use ChromeOS built-in backup.
