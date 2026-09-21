"""NPM / Yarn command builder for TypeSafe speculative fan-out responses."""

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


def _detect_pkg_manager(context: dict[str, Any] | Any, query: str) -> str:
    """Detect npm, yarn, or pnpm from workspace files or explicit query."""
    if re.search(r'\byarn\b', query, re.IGNORECASE):
        return "yarn"
    if re.search(r'\bpnpm\b', query, re.IGNORECASE):
        return "pnpm"
    if re.search(r'\bbun\b', query, re.IGNORECASE):
        return "bun"

    files: list[str] = []
    if isinstance(context, dict):
        files = context.get("files", [])
    elif hasattr(context, "files"):
        files = getattr(context, "files", []) or []

    if "yarn.lock" in files:
        return "yarn"
    if "pnpm-lock.yaml" in files:
        return "pnpm"
    if "bun.lockb" in files:
        return "bun"
    return "npm"


def _extract_package_name(query: str) -> str | None:
    """Extract package name(s) while filtering out flags."""
    raw = extract_from_query(
        query,
        r'(?:install|add|i|uninstall|remove|rm|update|upgrade)\s+([@a-zA-Z0-9_\-\.\/\s]+)',
    )
    if not raw:
        return None

    # Remove known flags and options
    tokens = raw.strip().split()
    pkgs = [
        t for t in tokens
        if not t.startswith("-") and t.lower() not in (
            "package", "packages", "dependency", "dependencies", "globally", "dev", "save"
        )
    ]
    return " ".join(pkgs) if pkgs else None


def build(response: Any, context: dict[str, Any] | Any) -> list[str]:
    """Translate TypeSafe response and system context into npm/yarn shell commands."""
    query = _get_query(context)
    pm = _detect_pkg_manager(context, query)

    npm_cmd = _get_choice(response, "npm_cmd", default="list")
    has_package = _get_noul(response, "has_package_name")

    pkg_name = _extract_package_name(query) if (has_package or re.search(r'\b(install|add|uninstall|remove|update)\b', query, re.IGNORECASE)) else None

    is_dev = bool(re.search(r'\b(dev|--save-dev|-D)\b', query, re.IGNORECASE))
    is_global = bool(re.search(r'\b(global|globally|-g)\b', query, re.IGNORECASE))

    # 1. INSTALL
    if npm_cmd == "install":
        if pkg_name:
            if pm == "yarn":
                if is_global:
                    return [f"yarn global add {pkg_name}"]
                if is_dev:
                    return [f"yarn add -D {pkg_name}"]
                return [f"yarn add {pkg_name}"]
            elif pm == "pnpm":
                if is_global:
                    return [f"pnpm add -g {pkg_name}"]
                if is_dev:
                    return [f"pnpm add -D {pkg_name}"]
                return [f"pnpm add {pkg_name}"]
            elif pm == "bun":
                if is_dev:
                    return [f"bun add -d {pkg_name}"]
                return [f"bun add {pkg_name}"]
            else:
                if is_global:
                    return [f"npm install -g {pkg_name}"]
                if is_dev:
                    return [f"npm install --save-dev {pkg_name}"]
                return [f"npm install {pkg_name}"]
        else:
            if pm == "yarn":
                return ["yarn install"]
            elif pm == "pnpm":
                return ["pnpm install"]
            elif pm == "bun":
                return ["bun install"]
            return ["npm install"]

    # 2. UNINSTALL
    if npm_cmd == "uninstall":
        target_pkg = pkg_name or "<package>"
        if pm == "yarn":
            return [f"yarn remove {target_pkg}"]
        elif pm == "pnpm":
            return [f"pnpm remove {target_pkg}"]
        elif pm == "bun":
            return [f"bun remove {target_pkg}"]
        return [f"npm uninstall {target_pkg}"]

    # 3. RUN
    if npm_cmd == "run":
        script = extract_from_query(
            query,
            r'(?:run|script)\s+([a-zA-Z0-9_\-:]+)',
        )
        if not script:
            for common in ("dev", "build", "start", "test", "lint", "preview", "watch"):
                if re.search(rf'\b{common}\b', query, re.IGNORECASE):
                    script = common
                    break
        script = script or "build"

        if pm == "yarn":
            return [f"yarn {script}"]
        elif pm == "pnpm":
            return [f"pnpm run {script}"]
        elif pm == "bun":
            return [f"bun run {script}"]
        elif script in ("test", "start"):
            return [f"npm {script}"]
        return [f"npm run {script}"]

    # 4. INIT
    if npm_cmd == "init":
        auto_yes = bool(re.search(r'\b(yes|-y|defaults?)\b', query, re.IGNORECASE))
        flag = " -y" if auto_yes else ""
        if pm == "yarn":
            return [f"yarn init{flag}"]
        elif pm == "pnpm":
            return [f"pnpm init"]
        return [f"npm init{flag}"]

    # 5. UPDATE
    if npm_cmd == "update":
        if pkg_name:
            if pm == "yarn":
                return [f"yarn upgrade {pkg_name}"]
            elif pm == "pnpm":
                return [f"pnpm update {pkg_name}"]
            return [f"npm update {pkg_name}"]
        if pm == "yarn":
            return ["yarn upgrade"]
        elif pm == "pnpm":
            return ["pnpm update"]
        return ["npm update"]

    # 6. LIST
    if npm_cmd == "list":
        if pm == "yarn":
            return ["yarn list --depth=0"]
        elif pm == "pnpm":
            return ["pnpm list --depth=0"]
        return ["npm list --depth=0"]

    # 7. AUDIT
    if npm_cmd == "audit":
        if re.search(r'\bfix\b', query, re.IGNORECASE):
            return ["npm audit fix"]
        return ["npm audit"]

    # 8. PUBLISH
    if npm_cmd == "publish":
        if re.search(r'\bpublic\b', query, re.IGNORECASE):
            return ["npm publish --access public"]
        return ["npm publish"]

    # 9. NPX
    if npm_cmd == "npx":
        tool = extract_from_query(query, r'npx\s+(.+)')
        if not tool:
            tool = extract_from_query(
                query,
                r'(?:execute|run(?:\s+with\s+npx)?)\s+([a-zA-Z0-9_\-\.\/]+.*)',
            )
        if tool:
            return [f"npx {tool.strip()}"]
        return ["npx <package>"]

    # Default fallback
    return ["npm list --depth=0"]
