# macOS (Darwin) Skills
# BSD coreutils, zsh default, Homebrew package manager

- For in-place sed replacement, always use an empty extension argument: `sed -i '' 's/old/new/g'`.
- Never use `xargs -d`. Use `tr '\n' '\0' | xargs -0` instead.
- Never use `grep -P` (Perl regex). Use `grep -E` for extended regex.
- Use `ifconfig` or `ipconfig getifaddr en0` for local IP, not `ip addr`.
- DNS flush: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`.
- Open files/URLs with `open`, not `xdg-open`.
- Clipboard: use `pbcopy` and `pbpaste`.
- Package manager is `brew`. Install with `brew install <pkg>`.
- Service management uses `launchctl`, not `systemctl`.
- `readlink` does not support `-f` by default. Use `greadlink -f` (from coreutils) or `realpath`.
- `date` uses BSD syntax. For epoch: `date -r <epoch>`, not `date -d @<epoch>`.
- `stat` syntax differs: use `stat -f '%z' <file>` for size, not `stat -c '%s'`.
- Default shell is `zsh` since macOS Catalina.
- Use `diskutil` for disk operations, not `fdisk` or `parted`.
- `lsof -i :<port>` to find processes on a port.
- Wi-Fi control: `networksetup -setairportpower en0 off/on`.
- Route info: `route -n get default`, not `ip route`.
