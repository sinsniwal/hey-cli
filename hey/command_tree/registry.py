"""Command tree registry — maps bucket names to builder functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable
    from hey.context import SystemContext


# Registry populated lazily on first use
_REGISTRY: dict[str, Callable] | None = None


def _load_registry() -> dict[str, Callable]:
    """Import all bucket builders and register them."""
    from hey.command_tree.buckets.git import build as git_build
    from hey.command_tree.buckets.file_ops import build as file_build
    from hey.command_tree.buckets.docker import build as docker_build
    from hey.command_tree.buckets.npm_yarn import build as npm_build
    from hey.command_tree.buckets.python_env import build as python_build
    from hey.command_tree.buckets.system import build as system_build
    from hey.command_tree.buckets.network import build as network_build
    from hey.command_tree.buckets.search import build as search_build
    from hey.command_tree.buckets.compress import build as compress_build

    return {
        "git": git_build,
        "file": file_build,
        "docker": docker_build,
        "npm": npm_build,
        "python": python_build,
        "system": system_build,
        "network": network_build,
        "search": search_build,
        "compress": compress_build,
    }


def get_builder(bucket: str) -> Callable | None:
    """Return the build function for a named bucket, or None."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _load_registry()
    return _REGISTRY.get(bucket)


def list_buckets() -> list[str]:
    """Return all registered bucket names."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _load_registry()
    return list(_REGISTRY.keys())
