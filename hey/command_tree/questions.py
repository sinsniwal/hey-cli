"""All TypeSafe question definitions for the speculative fan-out call.

Every question that *might* be relevant is defined here so they can all
be batched into a single API request.  The engine reads only the answers
that match the chosen routing bucket.
"""

from __future__ import annotations

from typesafe_sdk import Choice, Noul, Score


# ---------------------------------------------------------------------------
# Stage 1 — How many commands?
# ---------------------------------------------------------------------------

def command_count_question() -> dict[str, Choice]:
    return {
        "command_count": Choice(
            instructions="Select how many separate shell commands are needed to accomplish this task",
            criteria={
                "one": "A single command accomplishes the entire task",
                "two": "Two commands must run in sequence",
                "three_plus": "Three or more commands must run in sequence",
            },
        ),
    }


# ---------------------------------------------------------------------------
# Stage 2 — Route to command bucket
# ---------------------------------------------------------------------------

BUCKET_CRITERIA: dict[str, str] = {
    "git": "Git version control (commit, push, pull, branch, merge, diff, log, stash, clone, rebase, reset, checkout, status, add, tag)",
    "file": "File and directory operations (cp, mv, rm, mkdir, touch, chmod, chown, ln, cat, head, tail, wc, ls)",
    "docker": "Docker containers (build, run, stop, rm, ps, logs, exec, compose up/down, images, pull, prune)",
    "npm": "Node.js / JavaScript packages (npm install/run/init, yarn add/run, pnpm, npx)",
    "python": "Python environment (pip install, venv, python run, pytest, uv)",
    "system": "System processes and monitoring (ps, kill, top, df, du, env, export, whoami, uname, free, uptime)",
    "network": "Network operations (curl, wget, ssh, scp, rsync, ping, netstat, lsof, nslookup, dig)",
    "search": "Search and text processing (grep, find, awk, sed, sort, uniq, xargs, wc, locate, ag, rg)",
    "compress": "Compression and archives (tar, zip, unzip, gzip, gunzip, bzip2, 7z)",
}


def bucket_question() -> dict[str, Choice]:
    return {
        "bucket": Choice(
            instructions="Which command-line tool category best matches this task",
            criteria=BUCKET_CRITERIA,
        ),
    }


# ---------------------------------------------------------------------------
# Stage 3 — Sub-command per bucket (speculative: all asked at once)
# ---------------------------------------------------------------------------

GIT_COMMANDS: dict[str, str] = {
    "add": "Stage files for commit (git add)",
    "commit": "Record staged changes (git commit)",
    "push": "Upload commits to remote (git push)",
    "pull": "Download and merge from remote (git pull)",
    "checkout": "Switch branches or restore files (git checkout / git switch)",
    "branch": "Create, list, or delete branches (git branch)",
    "merge": "Merge branches together (git merge)",
    "stash": "Temporarily store uncommitted changes (git stash)",
    "log": "View commit history (git log)",
    "diff": "Show file changes (git diff)",
    "reset": "Undo commits or unstage files (git reset)",
    "clone": "Clone a remote repository (git clone)",
    "status": "Show working tree status (git status)",
    "rebase": "Reapply commits on another base (git rebase)",
    "tag": "Create, list, or delete tags (git tag)",
}

FILE_COMMANDS: dict[str, str] = {
    "copy": "Copy files or directories (cp)",
    "move_rename": "Move or rename files/directories (mv)",
    "delete": "Remove files or directories (rm)",
    "create_dir": "Create directories (mkdir)",
    "create_file": "Create empty file (touch)",
    "permissions": "Change permissions or ownership (chmod, chown)",
    "read": "Display file contents (cat, head, tail, less)",
    "link": "Create symbolic or hard links (ln)",
    "list": "List directory contents (ls)",
    "count": "Count lines, words, or characters (wc)",
}

DOCKER_COMMANDS: dict[str, str] = {
    "build": "Build an image from a Dockerfile (docker build)",
    "run": "Create and start a container (docker run)",
    "stop": "Stop running containers (docker stop)",
    "rm": "Remove containers (docker rm)",
    "ps": "List containers (docker ps)",
    "logs": "View container logs (docker logs)",
    "exec": "Run a command in a running container (docker exec)",
    "compose_up": "Start services with Docker Compose (docker compose up)",
    "compose_down": "Stop services with Docker Compose (docker compose down)",
    "images": "List images (docker images)",
    "pull": "Pull an image from a registry (docker pull)",
    "prune": "Remove unused data (docker system prune)",
}

NPM_COMMANDS: dict[str, str] = {
    "install": "Install packages (npm install, yarn add, pnpm add)",
    "uninstall": "Remove packages (npm uninstall, yarn remove)",
    "run": "Run a script from package.json (npm run, yarn run)",
    "init": "Initialize a new project (npm init, yarn init)",
    "update": "Update packages (npm update, yarn upgrade)",
    "list": "List installed packages (npm list, yarn list)",
    "audit": "Check for vulnerabilities (npm audit)",
    "publish": "Publish a package (npm publish)",
    "npx": "Execute a package binary (npx)",
}

PYTHON_COMMANDS: dict[str, str] = {
    "pip_install": "Install Python packages (pip install)",
    "pip_uninstall": "Uninstall Python packages (pip uninstall)",
    "pip_freeze": "List installed packages (pip freeze, pip list)",
    "venv_create": "Create a virtual environment (python -m venv)",
    "venv_activate": "Activate a virtual environment (source .venv/bin/activate)",
    "run_script": "Run a Python script (python script.py)",
    "pytest": "Run tests (pytest, python -m pytest)",
    "pip_upgrade": "Upgrade packages (pip install --upgrade)",
}

SYSTEM_COMMANDS: dict[str, str] = {
    "ps": "List running processes (ps aux, ps -ef)",
    "kill": "Kill a process (kill, kill -9, killall)",
    "df": "Show disk space usage (df -h)",
    "du": "Show directory sizes (du -sh)",
    "env": "Show or set environment variables (env, export, printenv)",
    "whoami": "Show current user (whoami, id)",
    "uname": "Show system information (uname -a)",
    "uptime": "Show system uptime (uptime)",
    "top": "Show running processes interactively (top, htop)",
    "history": "Show command history (history)",
}

NETWORK_COMMANDS: dict[str, str] = {
    "curl": "Make HTTP requests (curl)",
    "wget": "Download files (wget)",
    "ssh": "Connect to remote host (ssh)",
    "scp": "Copy files to/from remote (scp)",
    "rsync": "Synchronize files (rsync)",
    "ping": "Test network connectivity (ping)",
    "lsof_port": "Find process using a port (lsof -i, netstat)",
    "dns": "DNS lookup (nslookup, dig, host)",
}

SEARCH_COMMANDS: dict[str, str] = {
    "grep": "Search file contents for a pattern (grep)",
    "find": "Find files by name or attributes (find)",
    "sed": "Stream editor for text transformation (sed)",
    "awk": "Pattern scanning and processing (awk)",
    "sort": "Sort lines of text (sort, sort -u)",
    "xargs": "Build and execute commands from input (xargs)",
    "wc": "Count lines, words, characters (wc)",
}

COMPRESS_COMMANDS: dict[str, str] = {
    "tar_create": "Create a tar archive (tar -czf)",
    "tar_extract": "Extract a tar archive (tar -xzf)",
    "zip_create": "Create a zip archive (zip -r)",
    "zip_extract": "Extract a zip archive (unzip)",
    "gzip": "Compress a file (gzip)",
    "gunzip": "Decompress a file (gunzip)",
}


def sub_command_questions() -> dict[str, Choice]:
    """All sub-command choices — asked speculatively."""
    return {
        "git_cmd": Choice(instructions="Which git operation is being requested", criteria=GIT_COMMANDS),
        "file_cmd": Choice(instructions="Which file operation is being requested", criteria=FILE_COMMANDS),
        "docker_cmd": Choice(instructions="Which Docker operation is being requested", criteria=DOCKER_COMMANDS),
        "npm_cmd": Choice(instructions="Which npm/yarn operation is being requested", criteria=NPM_COMMANDS),
        "python_cmd": Choice(instructions="Which Python operation is being requested", criteria=PYTHON_COMMANDS),
        "system_cmd": Choice(instructions="Which system operation is being requested", criteria=SYSTEM_COMMANDS),
        "network_cmd": Choice(instructions="Which network operation is being requested", criteria=NETWORK_COMMANDS),
        "search_cmd": Choice(instructions="Which search/text operation is being requested", criteria=SEARCH_COMMANDS),
        "compress_cmd": Choice(instructions="Which compression operation is being requested", criteria=COMPRESS_COMMANDS),
    }


# ---------------------------------------------------------------------------
# Stage 4 — Flag and argument questions (speculative)
# ---------------------------------------------------------------------------

def flag_questions(
    branches: list[str],
    files: list[str],
) -> dict[str, Choice | Noul | Score]:
    """Flag/argument questions — all asked speculatively in one call."""
    qs: dict[str, Choice | Noul | Score] = {}

    # -- Git flags --
    qs["git_force"] = Noul(instructions="The user wants to force push, overwriting remote history")
    qs["git_set_upstream"] = Noul(instructions="The user wants to set the upstream tracking branch")
    qs["git_amend"] = Noul(instructions="The user wants to amend the previous commit instead of creating a new one")
    qs["git_commit_all"] = Noul(instructions="The user wants to commit all tracked modified files without explicit staging")
    qs["git_stash_pop"] = Noul(instructions="The user wants to pop (apply and remove) the stash, not just apply it")

    if branches:
        qs["git_target_branch"] = Choice(
            instructions="Which branch is the target of this git operation",
            criteria={b: f"Branch: {b}" for b in branches[:30]},
        )

    # -- File flags --
    qs["file_recursive"] = Noul(instructions="The operation should apply recursively to subdirectories")
    qs["file_force"] = Noul(instructions="The operation should proceed without prompting for confirmation")
    qs["file_create_parents"] = Noul(instructions="Parent directories should be created if they do not exist")

    # -- Docker flags --
    qs["docker_all"] = Noul(instructions="The Docker operation should apply to all containers or images, not just one")
    qs["docker_detach"] = Noul(instructions="The Docker container should run in detached background mode")
    qs["docker_follow"] = Noul(instructions="The user wants to follow or stream the output continuously")

    # -- Search flags --
    qs["search_recursive"] = Noul(instructions="The search should include subdirectories recursively")
    qs["search_case_insensitive"] = Noul(instructions="The search should be case-insensitive")
    qs["search_count_only"] = Noul(instructions="The user only wants a count of matches, not the matches themselves")

    # -- Target file from CWD listing --
    if files:
        qs["target_file"] = Choice(
            instructions="Which file or directory in the current listing is the primary target of this operation",
            criteria={f: f"File/dir: {f}" for f in files[:50]},
        )

    # -- Free-text argument hint --
    # For arguments that can't be enumerated (URLs, package names, patterns),
    # we ask what *kind* of argument it is, then extract it from the query in code.
    qs["has_url_arg"] = Noul(instructions="The user query contains a URL that should be used as an argument")
    qs["has_package_name"] = Noul(instructions="The user query contains a package or library name to install or remove")
    qs["has_search_pattern"] = Noul(instructions="The user query contains a search pattern, regex, or text to find")
    qs["has_port_number"] = Noul(instructions="The user query mentions a specific network port number")

    return qs


# ---------------------------------------------------------------------------
# Safety assessment
# ---------------------------------------------------------------------------

def safety_question() -> dict[str, Score]:
    return {
        "destructive_risk": Score(
            instructions="Rate the safety risk of executing this shell command unattended",
            criteria=[
                "Safe: read-only or idempotent command (ls, cat, echo, mkdir -p, git status, git log)",
                "Moderate: non-idempotent write that can be undone (mv, git commit, kill single process, chmod)",
                "Dangerous: irreversible deletion or destructive operation (rm -rf, force push, dd, mkfs, drop database)",
            ],
        ),
    }
