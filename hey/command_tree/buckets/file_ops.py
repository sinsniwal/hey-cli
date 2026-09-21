"""File operations command builder for TypeSafe speculative fan-out responses."""

from __future__ import annotations

import re
from typing import Any

NOUL_THRESHOLD = 0.6


def _get_choice(response: Any, key: str, default: str = "") -> str:
    """Safely get a Choice answer from the TypeSafe response."""
    try:
        choices = getattr(response, "choices", None)
        if choices is None and isinstance(response, dict):
            choices = response.get("choices")
        if isinstance(choices, dict):
            item = choices.get(key)
            if item is not None:
                val = getattr(item, "choice", None)
                if val is None and isinstance(item, dict):
                    val = item.get("choice")
                if val is not None:
                    return str(val)
    except Exception:
        pass
    return default


def _get_noul(response: Any, key: str, threshold: float = NOUL_THRESHOLD) -> bool:
    """Safely check if a Noul probability meets or exceeds the threshold."""
    try:
        nouls = getattr(response, "nouls", None)
        if nouls is None and isinstance(response, dict):
            nouls = response.get("nouls")
        if isinstance(nouls, dict):
            item = nouls.get(key)
            if item is not None:
                val = getattr(item, "noul", None)
                if val is None and isinstance(item, dict):
                    val = item.get("noul")
                if val is not None:
                    return float(val) >= threshold
    except Exception:
        pass
    return False


def _get_query(context: dict[str, Any] | Any) -> str:
    """Extract query string from context if available."""
    if isinstance(context, dict):
        for k in ("query", "user_query", "raw_query", "prompt"):
            val = context.get(k)
            if val:
                return str(val)
    elif hasattr(context, "query"):
        val = getattr(context, "query")
        if val:
            return str(val)
    return ""


def extract_from_query(query: str, pattern: str) -> str | None:
    """Extract captured regex group from query string."""
    if not query:
        return None
    match = re.search(pattern, query, re.IGNORECASE)
    return match.group(1) if match else None


def build(response: Any, context: dict[str, Any] | Any) -> list[str]:
    """Translate TypeSafe response and system context into file operation shell commands."""
    query = _get_query(context)

    file_cmd = _get_choice(response, "file_cmd", default="list")
    recursive = _get_noul(response, "file_recursive")
    force = _get_noul(response, "file_force")
    create_parents = _get_noul(response, "file_create_parents")
    target_file = _get_choice(response, "target_file", default="")

    # 1. COPY (cp)
    if file_cmd == "copy":
        pair_match = re.search(
            r'(?:copy|cp)\s+([^\s]+)\s+(?:to\s+|into\s+)?([^\s]+)',
            query,
            re.IGNORECASE,
        )
        src = pair_match.group(1) if pair_match else (target_file or "<source>")
        dest = pair_match.group(2) if pair_match else (f"{src}.bak" if src != "<source>" else "<dest>")

        flags: list[str] = []
        if recursive:
            flags.append("-r")
        if force:
            flags.append("-f")

        flag_str = f" {' '.join(flags)}" if flags else ""
        return [f"cp{flag_str} {src} {dest}"]

    # 2. MOVE / RENAME (mv)
    if file_cmd == "move_rename":
        pair_match = re.search(
            r'(?:move|rename|mv)\s+([^\s]+)\s+(?:to\s+|into\s+|as\s+)?([^\s]+)',
            query,
            re.IGNORECASE,
        )
        src = pair_match.group(1) if pair_match else (target_file or "<source>")
        dest = pair_match.group(2) if pair_match else "<destination>"

        flag_str = " -f" if force else ""
        return [f"mv{flag_str} {src} {dest}"]

    # 3. DELETE (rm)
    if file_cmd == "delete":
        target = target_file
        if not target:
            target = extract_from_query(
                query,
                r'(?:rm|remove|delete)\s+(?:-rf?\s+)?([^\s]+)',
            ) or "<target>"

        if recursive and force:
            return [f"rm -rf {target}"]
        if recursive:
            return [f"rm -r {target}"]
        if force:
            return [f"rm -f {target}"]
        return [f"rm {target}"]

    # 4. CREATE_DIR (mkdir)
    if file_cmd == "create_dir":
        dirname = extract_from_query(
            query,
            r'(?:mkdir|create(?:\s+a)?\s+dir(?:ectory)?|folder)\s+([^\s]+)',
        ) or target_file or "<directory>"

        if create_parents or "/" in dirname or "\\" in dirname:
            return [f"mkdir -p {dirname}"]
        return [f"mkdir {dirname}"]

    # 5. CREATE_FILE (touch)
    if file_cmd == "create_file":
        filename = extract_from_query(
            query,
            r'(?:touch|create(?:\s+a)?\s+file)\s+([^\s]+)',
        ) or target_file or "<filename>"
        return [f"touch {filename}"]

    # 6. PERMISSIONS (chmod)
    if file_cmd == "permissions":
        mode = extract_from_query(
            query,
            r'(?:chmod\s+|permissions?\s+(?:to\s+)?)([0-7]{3,4}|\+[a-z]+|[a-z]+\+[a-z]+)',
        ) or "+x"
        target = target_file
        if not target:
            target = extract_from_query(
                query,
                r'(?:on|for|file)\s+([^\s]+)',
            ) or "<file>"

        flag_str = " -R" if recursive else ""
        return [f"chmod{flag_str} {mode} {target}"]

    # 7. READ (cat, head, tail)
    if file_cmd == "read":
        target = target_file
        if not target:
            target = extract_from_query(
                query,
                r'(?:cat|read|show|view|display|head|tail)\s+(?:(?:contents?|lines?)(?:\s+of)?\s+|(?:of|for|in|from)\s+)?([^\s]+)',
            )
        if not target or target.lower() in ("of", "for", "in", "the", "a", "file", "content"):
            target = "<file>"

        if re.search(r'\b(follow|-f)\b', query, re.IGNORECASE):
            return [f"tail -f {target}"]
        if re.search(r'\btail\b', query, re.IGNORECASE):
            lines = extract_from_query(query, r'(?:-n|last)\s*(\d+)') or "20"
            return [f"tail -n {lines} {target}"]
        if re.search(r'\bhead\b', query, re.IGNORECASE):
            lines = extract_from_query(query, r'(?:-n|first)\s*(\d+)') or "20"
            return [f"head -n {lines} {target}"]
        return [f"cat {target}"]

    # 8. LINK (ln)
    if file_cmd == "link":
        pair_match = re.search(
            r'(?:link|ln)\s+(?:-s\s+)?([^\s]+)\s+(?:to\s+)?([^\s]+)',
            query,
            re.IGNORECASE,
        )
        src = pair_match.group(1) if pair_match else (target_file or "<source>")
        dest = pair_match.group(2) if pair_match else "<symlink>"

        flag = "-sf" if force else "-s"
        return [f"ln {flag} {src} {dest}"]

    # 9. LIST (ls)
    if file_cmd == "list":
        flags = ["-la"]
        if recursive:
            flags.append("-R")
        target_part = f" {target_file}" if target_file else ""
        return [f"ls {' '.join(flags)}{target_part}"]

    # 10. COUNT (wc)
    if file_cmd == "count":
        target = target_file
        if not target:
            target = extract_from_query(
                query,
                r'(?:count|wc)\s+(?:(?:lines?|words?|bytes?|chars?|characters?)\s+(?:in\s+|of\s+|for\s+)?|(?:in|of|for)\s+)?([^\s]+)',
            )
        if not target or target.lower() in ("words", "word", "lines", "line", "bytes", "byte", "chars", "characters", "in", "of", "for", "the", "a"):
            target = "*"

        if re.search(r'\b(words?|-w)\b', query, re.IGNORECASE):
            return [f"wc -w {target}"]
        if re.search(r'\b(bytes?|chars?|-c|-m)\b', query, re.IGNORECASE):
            return [f"wc -c {target}"]
        return [f"wc -l {target}"]

    # Default fallback
    return ["ls -la"]
