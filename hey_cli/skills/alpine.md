# Alpine Linux Skills
# BusyBox coreutils, ash shell, apk package manager

- Shell is `ash` (BusyBox), NOT `bash`. Bash must be installed separately: `apk add bash`.
- Coreutils are BusyBox stripped-down versions. Many GNU flags are missing.
- `sed -i` works but some advanced GNU sed features may not.
- `xargs -d` is NOT supported. Use `tr '\n' '\0' | xargs -0`.
- `grep -P` is NOT supported. Use `grep -E` for extended regex.
- Package manager: `apk add <pkg>`. Update: `apk update`. Upgrade: `apk upgrade`.
- Use `apk add --no-cache <pkg>` in Docker to avoid caching index locally.
- No `systemctl`. Service management: `rc-service <service> start/stop/restart`, `rc-update add <service>`.
- Uses `musl` libc instead of `glibc`. Some precompiled binaries may not work.
- Minimal base image (~5MB). Ideal for Docker containers.
- `nano` and `vim` are not installed by default. Install with `apk add nano` or `apk add vim`.
- Network tools: `ip addr` (if `iproute2` installed), otherwise `ifconfig` (from `busybox`).
- No `man` pages by default. Install `mandoc` and `<pkg>-doc` packages.
- `wget` is BusyBox version (limited). Install full `wget` with `apk add wget`.
