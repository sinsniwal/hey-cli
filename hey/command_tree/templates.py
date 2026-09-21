"""Command template builder — assembles final shell command strings."""

from __future__ import annotations


def join_parts(*parts: str) -> str:
    """Join non-empty command parts with spaces."""
    return " ".join(p for p in parts if p).strip()


def flag_if(condition: bool, flag: str) -> str:
    """Return the flag string if condition is True, else empty."""
    return flag if condition else ""


def quote_arg(arg: str) -> str:
    """Quote an argument if it contains spaces or special chars."""
    if not arg:
        return '""'
    if " " in arg or any(c in arg for c in "()[]{}|&;$`!#*?<>"):
        # Use single quotes, escaping any internal single quotes
        escaped = arg.replace("'", "'\\''")
        return f"'{escaped}'"
    return arg
