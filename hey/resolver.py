"""Resolve dynamic arguments (files, branches, containers, etc.).

This module gathers runtime data to feed as Choice options into the
TypeSafe question set.  All functions are designed to be fast (< 20ms each).
"""

from __future__ import annotations

import os
import subprocess


def _run(cmd: list[str], timeout: float = 2.0) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def list_files(directory: str = ".", max_entries: int = 50) -> list[str]:
    """List files and directories in the given path."""
    try:
        entries = sorted(os.listdir(directory))
        return entries[:max_entries]
    except OSError:
        return []


def list_git_branches(max_branches: int = 30) -> list[str]:
    """List local + remote git branches (deduplicated)."""
    raw = _run(["git", "branch", "-a", "--format=%(refname:short)"])
    if not raw:
        return ["main"]

    branches: list[str] = []
    seen: set[str] = set()
    for b in raw.splitlines():
        b = b.strip().replace("origin/", "")
        if b and "HEAD" not in b and b not in seen:
            seen.add(b)
            branches.append(b)
    return branches[:max_branches]


def list_docker_containers(running_only: bool = True) -> list[str]:
    """List Docker container names."""
    flag = "" if running_only else "-a"
    cmd = ["docker", "ps", "--format", "{{.Names}}"]
    if flag:
        cmd.insert(2, flag)
    raw = _run(cmd)
    return raw.splitlines() if raw else []


def list_docker_images() -> list[str]:
    """List Docker image repository:tag strings."""
    raw = _run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"])
    return [img for img in raw.splitlines() if img and "<none>" not in img][:30]


def find_files_by_extension(ext: str, max_results: int = 20) -> list[str]:
    """Find files matching an extension using find command."""
    raw = _run(["find", ".", "-maxdepth", "3", "-name", f"*.{ext}", "-type", "f"])
    if not raw:
        return []
    return raw.splitlines()[:max_results]


def find_process_on_port(port: int) -> list[str]:
    """Find process IDs listening on a given port."""
    raw = _run(["lsof", "-ti", f":{port}"])
    return raw.splitlines() if raw else []
