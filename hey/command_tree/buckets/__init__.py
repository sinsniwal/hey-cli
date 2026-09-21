"""Command bucket package."""

from __future__ import annotations

from typing import Any, Callable

from hey.command_tree.buckets import (
    compress,
    docker,
    file_ops,
    git,
    network,
    npm_yarn,
    python_env,
    search,
    system,
)

BUCKET_BUILDERS: dict[str, Callable[[Any, dict[str, Any] | Any], list[str]]] = {
    "git": git.build,
    "file": file_ops.build,
    "docker": docker.build,
    "npm": npm_yarn.build,
    "python": python_env.build,
    "system": system.build,
    "network": network.build,
    "search": search.build,
    "compress": compress.build,
}

__all__ = [
    "BUCKET_BUILDERS",
    "compress",
    "docker",
    "file_ops",
    "git",
    "network",
    "npm_yarn",
    "python_env",
    "search",
    "system",
]
