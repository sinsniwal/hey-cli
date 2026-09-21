"""Gather local system context to feed into TypeSafe state.

All context is gathered eagerly and fast (< 50ms target) so it can be
included in the single speculative-fan-out API call.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from hey.config import detect_os, detect_shell


MAX_FILES = 50  # Cap directory listing to keep state small


@dataclass
class SystemContext:
    """Snapshot of the local environment at invocation time."""

    cwd: str = ""
    os_type: str = ""
    shell: str = ""
    files: list[str] = field(default_factory=list)
    is_git_repo: bool = False
    git_branch: str = ""
    git_status: str = ""
    git_branches: list[str] = field(default_factory=list)

    def to_state_dict(self) -> dict:
        """Convert to a dict suitable for TypeSafe ``state``."""
        d: dict = {
            "cwd": self.cwd,
            "os": self.os_type,
            "shell": self.shell,
            "files_in_cwd": self.files,
        }
        if self.is_git_repo:
            d["git_branch"] = self.git_branch
            d["git_status"] = self.git_status
            d["git_branches"] = self.git_branches
        return d


def _run(cmd: list[str], timeout: float = 2.0) -> str:
    """Run a command and return stripped stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=None,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def gather_context(include_git: bool = True) -> SystemContext:
    """Collect local system context.  Designed to be fast (< 50ms)."""
    ctx = SystemContext()
    ctx.cwd = os.getcwd()
    ctx.os_type = detect_os()
    ctx.shell = detect_shell()

    # --- Directory listing (capped) ---
    try:
        entries = sorted(os.listdir("."))[:MAX_FILES]
        ctx.files = entries
    except OSError:
        ctx.files = []

    # --- Git context (only if .git exists) ---
    if include_git and Path(".git").is_dir():
        ctx.is_git_repo = True
        ctx.git_branch = _run(["git", "branch", "--show-current"])
        ctx.git_status = _run(["git", "status", "--porcelain"])

        raw_branches = _run(
            ["git", "branch", "-a", "--format=%(refname:short)"]
        )
        if raw_branches:
            branches = [
                b.replace("origin/", "")
                for b in raw_branches.splitlines()
                if b and "HEAD" not in b
            ]
            # Deduplicate while preserving order
            seen: set[str] = set()
            unique: list[str] = []
            for b in branches:
                if b not in seen:
                    seen.add(b)
                    unique.append(b)
            ctx.git_branches = unique[:30]  # cap
        else:
            ctx.git_branches = ["main"]

    return ctx


def generate_commit_message(max_files: int = 3) -> str:
    """Auto-generate a commit message from ``git diff --stat``.

    Format: "Update app.js, Add config.yaml, Delete old.txt"
    Falls back to "Update changes" if git info unavailable.
    """
    diff_stat = _run(["git", "diff", "--cached", "--stat"])
    if not diff_stat:
        diff_stat = _run(["git", "diff", "--stat"])
    if not diff_stat:
        return "Update changes"

    lines = diff_stat.strip().splitlines()
    # Last line is the summary; preceding lines are file changes
    file_lines = [l.strip() for l in lines[:-1] if "|" in l]

    parts: list[str] = []
    for fl in file_lines[:max_files]:
        # Format: "src/app.js | 5 ++-"
        fname = fl.split("|")[0].strip()
        change_info = fl.split("|")[1].strip() if "|" in fl else ""

        if "+" in change_info and "-" not in change_info:
            parts.append(f"Add {fname}")
        elif "-" in change_info and "+" not in change_info:
            parts.append(f"Remove {fname}")
        else:
            parts.append(f"Update {fname}")

    if not parts:
        return "Update changes"

    remaining = len(file_lines) - max_files
    msg = ", ".join(parts)
    if remaining > 0:
        msg += f" (+{remaining} more)"
    return msg
