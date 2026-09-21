"""Docker command builder for TypeSafe speculative fan-out responses."""

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
    """Translate TypeSafe response and system context into Docker shell commands."""
    query = _get_query(context)

    docker_cmd = _get_choice(response, "docker_cmd", default="ps")
    docker_all = _get_noul(response, "docker_all")
    docker_detach = _get_noul(response, "docker_detach")
    docker_follow = _get_noul(response, "docker_follow")

    # 1. BUILD
    if docker_cmd == "build":
        tag = extract_from_query(
            query,
            r'(?:tag|-t)\s+([a-zA-Z0-9_\-\.\/:]+)',
        )
        if not tag:
            tag = extract_from_query(query, r'build\s+(?:image\s+)?([a-zA-Z0-9_\-\.\/:]+)')
            if tag in (".", "image", "container"):
                tag = None
        if tag:
            return [f"docker build -t {tag} ."]
        return ["docker build ."]

    # 2. RUN
    if docker_cmd == "run":
        image = extract_from_query(
            query,
            r'(?:run|start)\s+(?:container\s+)?(?:from\s+)?([a-zA-Z0-9_\-\.\/:]+)',
        ) or "<image>"

        port = extract_from_query(query, r'(?:port|-p)\s+([0-9]+(?::[0-9]+)?)')
        name = extract_from_query(query, r'(?:--name|named)\s+([a-zA-Z0-9_\-]+)')

        flags: list[str] = []
        if docker_detach:
            flags.append("-d")
        if re.search(r'\b(--rm|remove|ephemeral)\b', query, re.IGNORECASE):
            flags.append("--rm")
        if port:
            port_arg = port if ":" in port else f"{port}:{port}"
            flags.extend(["-p", port_arg])
        if name:
            flags.extend(["--name", name])

        flag_str = f" {' '.join(flags)}" if flags else ""
        return [f"docker run{flag_str} {image}"]

    # 3. STOP
    if docker_cmd == "stop":
        if docker_all or re.search(r'\ball\b', query, re.IGNORECASE):
            return ["docker stop $(docker ps -q)"]
        container = extract_from_query(
            query,
            r'(?:stop|kill)\s+(?:container\s+)?([a-zA-Z0-9_\-]+)',
        )
        if container and container not in ("all", "container", "containers"):
            return [f"docker stop {container}"]
        return ["docker stop $(docker ps -q)"]

    # 4. RM
    if docker_cmd == "rm":
        if docker_all or re.search(r'\ball\b', query, re.IGNORECASE):
            return ["docker rm -f $(docker ps -a -q)"]
        container = extract_from_query(
            query,
            r'(?:rm|remove|delete)\s+(?:container\s+)?([a-zA-Z0-9_\-]+)',
        )
        if container and container not in ("all", "container", "containers"):
            flag = " -f" if re.search(r'\b(force|-f)\b', query, re.IGNORECASE) else ""
            return [f"docker rm{flag} {container}"]
        return ["docker rm $(docker ps -a -q)"]

    # 5. PS
    if docker_cmd == "ps":
        if docker_all or re.search(r'\ball\b', query, re.IGNORECASE):
            return ["docker ps -a"]
        return ["docker ps"]

    # 6. LOGS
    if docker_cmd == "logs":
        container = extract_from_query(
            query,
            r'logs?(?:\s+for|\s+of)?\s+([a-zA-Z0-9_\-]+)',
        ) or "<container>"

        if docker_follow or re.search(r'\b(follow|-f)\b', query, re.IGNORECASE):
            return [f"docker logs -f {container}"]
        return [f"docker logs --tail 100 {container}"]

    # 7. EXEC
    if docker_cmd == "exec":
        container = extract_from_query(
            query,
            r'exec\s+(?:in\s+)?([a-zA-Z0-9_\-]+)',
        ) or "<container>"
        cmd_arg = extract_from_query(
            query,
            r'exec\s+[a-zA-Z0-9_\-]+\s+(.+)',
        ) or "/bin/sh"

        if docker_detach:
            return [f"docker exec -d {container} {cmd_arg}"]
        return [f"docker exec -it {container} {cmd_arg}"]

    # 8. COMPOSE_UP
    if docker_cmd == "compose_up":
        if docker_detach or re.search(r'\b(detach|background|-d)\b', query, re.IGNORECASE):
            return ["docker compose up -d"]
        return ["docker compose up"]

    # 9. COMPOSE_DOWN
    if docker_cmd == "compose_down":
        if re.search(r'\b(volume|volumes|-v)\b', query, re.IGNORECASE):
            return ["docker compose down -v"]
        return ["docker compose down"]

    # 10. IMAGES
    if docker_cmd == "images":
        if docker_all:
            return ["docker images -a"]
        return ["docker images"]

    # 11. PULL
    if docker_cmd == "pull":
        image = extract_from_query(
            query,
            r'pull\s+(?:image\s+)?([a-zA-Z0-9_\-\.\/:]+)',
        ) or "<image>"
        return [f"docker pull {image}"]

    # 12. PRUNE
    if docker_cmd == "prune":
        if docker_all or re.search(r'\ball\b', query, re.IGNORECASE):
            return ["docker system prune -a --volumes -f"]
        return ["docker system prune -f"]

    # Default fallback
    return ["docker ps"]
