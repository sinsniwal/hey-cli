# Universal Shell Skills
# These apply across ALL operating systems and shells

## File Search Heuristics
- When asked to ignore "gitignore type files", aggressively exclude noisy directories like `.venv`, `.git`, `node_modules`, `__pycache__`, `venv`, `env`, `.tox`, `.mypy_cache`, `.pytest_cache`, `dist`, `build`, `.eggs`, `*.egg-info` using `grep --exclude-dir` or `find` prune flags, rather than relying strictly on `git ls-files` (the repo might be untracked).
- When searching for files by content, ALWAYS use `grep -r` (recursive) when targeting a directory. Without `-r`, grep will fail with "Is a directory".
- When searching for files by content, prefer `grep -r` with `--exclude-dir` over piping `find` to `xargs grep` for simpler queries.
- When counting occurrences of a word in files, use `grep -o '<word>' | wc -l` to count individual matches, not `grep -c` which counts lines.

## Command Output
- Do not pipe context-gathering commands to `/dev/null` if you intend to read their outputs.
- When output might be extremely long, pipe through `head -n 50` or `tail -n 50` to avoid flooding.
- Always use `2>&1` when you need to capture both stdout and stderr.

## File Operations
- Always quote paths and variables to handle spaces: `"$HOME/my folder"` not `$HOME/my folder`.
- Use `mkdir -p` to create nested directories without errors if they exist.
- Prefer `&&` chaining over `;` to stop on first failure.

## Process Management
- To find a process on a specific port: `lsof -i :<port>` works on both macOS and Linux.
- Use `kill -15` (SIGTERM) first, `kill -9` (SIGKILL) only as last resort.
- Background a command with `&`, bring back with `fg`.

## Git Operations
- `git status` is always safe and informative — use it to gather context.
- `git log --oneline -n 10` for recent commits without flooding.
- `git diff --stat` for a quick summary of changes.
- `git stash` before risky operations, `git stash pop` to restore.

## Docker Operations
- Check if Docker is running: `docker info > /dev/null 2>&1 && echo 'running' || echo 'not running'`.
- List containers: `docker ps` (running), `docker ps -a` (all).
- List images: `docker images`.
- Clean up: `docker system prune` (requires confirmation).

## Network Diagnostics
- Test connectivity: `ping -c 3 <host>` (use `-c` to limit count, don't let it run forever).
- Check if a port is reachable: `nc -zv <host> <port>` (works on macOS and most Linux).
- DNS lookup: `dig <domain>` or `nslookup <domain>`.

## Safety
- Never run `rm -rf /` or `rm -rf /*` under any circumstances.
- Always double-check destructive commands before executing.
- When in doubt about a path, `ls` it first to verify contents.
- Use `--dry-run` flags when available (e.g., `rsync --dry-run`).
