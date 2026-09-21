"""System monitoring and process command builder for TypeSafe speculative fan-out responses."""

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
    """Translate TypeSafe response and system context into system shell commands."""
    query = _get_query(context)

    system_cmd = _get_choice(response, "system_cmd", default="ps")
    has_port = _get_noul(response, "has_port_number")

    port = extract_from_query(query, r'(?:port|:)\s*([0-9]{2,5})')

    # 1. PS
    if system_cmd == "ps":
        proc_name = extract_from_query(
            query,
            r'(?:process\s+(?:named|called|for)\s+|named\s+|called\s+|process\s+|running\s+|find\s+)([a-zA-Z0-9_\-\.]+)',
        )
        if proc_name and proc_name.lower() in ("named", "called", "running", "for", "the", "a"):
            proc_name = extract_from_query(query, rf'{proc_name}\s+([a-zA-Z0-9_\-\.]+)')
        if proc_name and proc_name.lower() not in ("all", "list", "processes", "process"):
            return [f"ps aux | grep {proc_name}"]
        return ["ps aux"]

    # 2. KILL
    if system_cmd == "kill":
        if (has_port or port) and port:
            return [f"kill -9 $(lsof -t -i:{port})"]

        pid = extract_from_query(
            query,
            r'(?:kill\s+|pid\s+|-9\s+|process\s+)([0-9]{2,6})',
        )
        if pid:
            return [f"kill -9 {pid}"]

        proc_name = extract_from_query(
            query,
            r'(?:kill|killall|stop|terminate)\s+([a-zA-Z0-9_\-\.]+)',
        )
        if proc_name and proc_name.lower() not in ("process", "all", "port"):
            return [f"pkill -f {proc_name}"]

        return ["kill -9 <pid>"]

    # 3. DF
    if system_cmd == "df":
        return ["df -h"]

    # 4. DU
    if system_cmd == "du":
        target = extract_from_query(
            query,
            r'(?:size(?:\s+of)?|du)\s+([^\s]+)',
        )
        if target and target.lower() not in ("all", "directory", "disk"):
            return [f"du -sh {target}"]
        return ["du -sh *"]

    # 5. ENV
    if system_cmd == "env":
        # Check if setting an env var
        export_match = re.search(r'export\s+([a-zA-Z_][a-zA-Z0-9_]*=.*)', query, re.IGNORECASE)
        if export_match:
            return [f"export {export_match.group(1)}"]

        # Check if inspecting a specific var
        var_name = extract_from_query(
            query,
            r'(?:echo|print|show|variable|var)\s+\$?([A-Z_][A-Z0-9_]+)',
        )
        if var_name:
            return [f"echo ${var_name}"]

        return ["env"]

    # 6. WHOAMI
    if system_cmd == "whoami":
        return ["whoami"]

    # 7. UNAME
    if system_cmd == "uname":
        return ["uname -a"]

    # 8. UPTIME
    if system_cmd == "uptime":
        return ["uptime"]

    # 9. TOP
    if system_cmd == "top":
        if re.search(r'\bhtop\b', query, re.IGNORECASE):
            return ["htop"]
        return ["top"]

    # 10. HISTORY
    if system_cmd == "history":
        term = extract_from_query(
            query,
            r'(?:history\s+(?:grep|for|search|matching)?|grep|search)\s+(?:for\s+|matching\s+)?([a-zA-Z0-9_\-\.]+)',
        )
        if term and term.lower() in ("grep", "search", "for", "matching"):
            term = extract_from_query(query, rf'{term}\s+([a-zA-Z0-9_\-\.]+)')
        if term and term.lower() not in ("command", "commands", "history", "all", "grep", "search"):
            return [f"history | grep {term}"]
        return ["history"]

    # Default fallback
    return ["ps aux"]
