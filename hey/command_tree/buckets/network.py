"""Network command builder for TypeSafe speculative fan-out responses."""

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


def _extract_url(query: str) -> str | None:
    """Extract URL or domain endpoint from query."""
    url = extract_from_query(query, r'((?:https?://|ftp://)[^\s\'">]+)')
    if not url:
        url = extract_from_query(
            query,
            r'(?:url|from|get|curl|fetch|download|wget)\s+([a-zA-Z0-9_\-\.\/:]+\.[a-zA-Z]{2,}[^\s\'"]*)',
        )
        if url and not url.startswith(("http://", "https://")):
            url = f"https://{url}"
    return url.rstrip(".,;)") if url else None


def _extract_port(query: str) -> str | None:
    """Extract port number from query."""
    return extract_from_query(query, r'(?:port|:)\s*([0-9]{2,5})')


def build(response: Any, context: dict[str, Any] | Any) -> list[str]:
    """Translate TypeSafe response and system context into network shell commands."""
    query = _get_query(context)

    network_cmd = _get_choice(response, "network_cmd", default="curl")
    has_url = _get_noul(response, "has_url_arg")
    has_port = _get_noul(response, "has_port_number")

    url = _extract_url(query) if (has_url or re.search(r'\b(http|url|download|curl|wget)\b', query, re.IGNORECASE)) else _extract_url(query)
    port = _extract_port(query) if (has_port or re.search(r'\b(port|lsof|listen)\b', query, re.IGNORECASE)) else _extract_port(query)

    # 1. CURL
    if network_cmd == "curl":
        target_url = url or "https://example.com"
        if re.search(r'\b(headers?|head|-I)\b', query, re.IGNORECASE):
            return [f"curl -I {target_url}"]
        if re.search(r'\bpost\b', query, re.IGNORECASE):
            json_body = extract_from_query(query, r'(\{.*\})')
            if json_body:
                safe_json = json_body.replace('"', '\\"')
                return [f'curl -X POST -H "Content-Type: application/json" -d "{safe_json}" {target_url}']
            return [f"curl -X POST {target_url}"]
        if re.search(r'\b(download|save|-O)\b', query, re.IGNORECASE):
            return [f"curl -O {target_url}"]
        return [f"curl -s {target_url}"]

    # 2. WGET
    if network_cmd == "wget":
        target_url = url or "https://example.com"
        return [f"wget {target_url}"]

    # 3. SSH
    if network_cmd == "ssh":
        host = extract_from_query(
            query,
            r'(?:ssh\s+|connect(?:\s+to)?\s+)([a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+|[a-zA-Z0-9_\-\.]+)',
        ) or "<user@host>"
        if port:
            return [f"ssh -p {port} {host}"]
        return [f"ssh {host}"]

    # 4. SCP
    if network_cmd == "scp":
        pair = re.search(
            r'scp\s+(?:-r\s+)?([^\s]+)\s+(?:to\s+)?([^\s]+)',
            query,
            re.IGNORECASE,
        )
        src = pair.group(1) if pair else "<source>"
        dest = pair.group(2) if pair else "<destination>"

        flags: list[str] = []
        if re.search(r'\b(recursive|-r|dir|folder)\b', query, re.IGNORECASE):
            flags.append("-r")
        if port:
            flags.extend(["-P", port])

        flag_str = f" {' '.join(flags)}" if flags else ""
        return [f"scp{flag_str} {src} {dest}"]

    # 5. RSYNC
    if network_cmd == "rsync":
        pair = re.search(
            r'rsync\s+([^\s]+)\s+(?:to\s+)?([^\s]+)',
            query,
            re.IGNORECASE,
        )
        src = pair.group(1) if pair else "<source>/"
        dest = pair.group(2) if pair else "<destination>/"

        flags = ["-avz", "--progress"]
        if re.search(r'\b(delete|remove)\b', query, re.IGNORECASE):
            flags.append("--delete")
        return [f"rsync {' '.join(flags)} {src} {dest}"]

    # 6. PING
    if network_cmd == "ping":
        host = extract_from_query(
            query,
            r'(?:ping\s+)([a-zA-Z0-9_\-\.]+)',
        )
        if not host or host in ("host", "server", "ip"):
            host = url.replace("https://", "").replace("http://", "").split("/")[0] if url else "8.8.8.8"
        return [f"ping -c 4 {host}"]

    # 7. LSOF_PORT
    if network_cmd == "lsof_port":
        target_port = port or "8080"
        if re.search(r'\b(kill|stop)\b', query, re.IGNORECASE):
            return [f"kill -9 $(lsof -t -i:{target_port})"]
        return [f"lsof -i :{target_port}"]

    # 8. DNS
    if network_cmd == "dns":
        domain = extract_from_query(
            query,
            r'(?:dns|lookup|dig|nslookup|resolve|host)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,})',
        )
        if not domain and url:
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        domain = domain or "example.com"

        if re.search(r'\bdig\b', query, re.IGNORECASE):
            return [f"dig {domain}"]
        return [f"nslookup {domain}"]

    # Default fallback
    return ["curl -I https://example.com"]
