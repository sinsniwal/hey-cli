# Fedora / RHEL / CentOS Skills
# GNU coreutils, bash default, dnf/yum package manager

- In-place sed: `sed -i 's/old/new/g'` (GNU).
- `xargs -d '\n'` and `grep -P` are supported.
- Package manager: `sudo dnf install <pkg>` (Fedora / RHEL 8+). Use `sudo yum install <pkg>` for RHEL 7 / CentOS 7.
- Service management: `sudo systemctl start/stop/restart/status <service>`.
- SELinux is enabled by default. Check with `getenforce`. Set permissive with `sudo setenforce 0`.
- SELinux contexts: use `ls -Z`, `chcon`, `restorecon`.
- Firewall: `sudo firewall-cmd --add-port=<port>/tcp --permanent && sudo firewall-cmd --reload`. Do NOT assume `ufw`.
- Low-level packages: `rpm -ivh <file>.rpm`, `rpm -qa` to list.
- `dnf` groups: `sudo dnf groupinstall "Development Tools"`.
- Network config: `ip addr`, `nmcli` for NetworkManager.
- DNS flush: `sudo systemd-resolve --flush-caches`.
- Open files/URLs: `xdg-open`.
- Clipboard: `xclip` or `xsel`.
- Journal logs: `journalctl -u <service> -f` for real-time logs.
