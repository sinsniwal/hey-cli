"""Python environment command builder for TypeSafe speculative fan-out responses."""

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


def _extract_python_package(query: str) -> str | None:
    """Extract python package name from query."""
    raw = extract_from_query(
        query,
        r'(?:install|uninstall|upgrade|add|remove|pip)\s+([a-zA-Z0-9_\-\.>=<,\s]+)',
    )
    if not raw:
        return None
    tokens = raw.strip().split()
    pkgs = [
        t for t in tokens
        if not t.startswith("-") and t.lower() not in (
            "package", "packages", "requirement", "requirements", "requirements.txt", "env", "venv"
        )
    ]
    return " ".join(pkgs) if pkgs else None


def build(response: Any, context: dict[str, Any] | Any) -> list[str]:
    """Translate TypeSafe response and system context into Python environment commands."""
    ctx_dict = context if isinstance(context, dict) else {}
    query = _get_query(context)
    files: list[str] = ctx_dict.get("files", [])
    os_type = str(ctx_dict.get("os_type", "")).lower()

    python_cmd = _get_choice(response, "python_cmd", default="pip_freeze")
    has_package = _get_noul(response, "has_package_name")

    pkg = _extract_python_package(query) if (has_package or re.search(r'\b(install|uninstall|upgrade)\b', query, re.IGNORECASE)) else None

    # 1. PIP_INSTALL
    if python_cmd == "pip_install":
        if re.search(r'\b(requirements?|-r)\b', query, re.IGNORECASE):
            return ["pip install -r requirements.txt"]
        if pkg:
            return [f"pip install {pkg}"]
        if "requirements.txt" in files:
            return ["pip install -r requirements.txt"]
        return ["pip install <package>"]

    # 2. PIP_UNINSTALL
    if python_cmd == "pip_uninstall":
        target = pkg or "<package>"
        return [f"pip uninstall -y {target}"]

    # 3. PIP_FREEZE
    if python_cmd == "pip_freeze":
        if re.search(r'\b(requirements?|save|export|write|file)\b', query, re.IGNORECASE):
            return ["pip freeze > requirements.txt"]
        return ["pip freeze"]

    # 4. VENV_CREATE
    if python_cmd == "venv_create":
        venv_name = extract_from_query(
            query,
            r'(?:venv|env|environment)\s+(?:named\s+)?([a-zA-Z0-9_\-\.]+)',
        )
        if not venv_name or venv_name in ("new", "a", "create"):
            venv_name = ".venv"
        return [f"python3 -m venv {venv_name}"]

    # 5. VENV_ACTIVATE
    if python_cmd == "venv_activate":
        venv_name = ".venv"
        if ".venv" not in files and "venv" in files:
            venv_name = "venv"
        elif "env" in files:
            venv_name = "env"

        if "windows" in os_type:
            return [rf"{venv_name}\Scripts\activate"]
        return [f"source {venv_name}/bin/activate"]

    # 6. RUN_SCRIPT
    if python_cmd == "run_script":
        script = extract_from_query(query, r'([a-zA-Z0-9_\-\.\/]+\.py)')
        if not script:
            target_file = _get_choice(response, "target_file", default="")
            if target_file and target_file.endswith(".py"):
                script = target_file
        if not script:
            for f in files:
                if f.endswith(".py") and f in ("main.py", "app.py", "run.py", "cli.py"):
                    script = f
                    break
        script = script or "main.py"
        return [f"python3 {script}"]

    # 7. PYTEST
    if python_cmd == "pytest":
        flags: list[str] = []
        if re.search(r'\b(verbose|-v)\b', query, re.IGNORECASE):
            flags.append("-v")
        if re.search(r'\b(coverage|cov)\b', query, re.IGNORECASE):
            flags.append("--cov")
        flag_str = f" {' '.join(flags)}" if flags else ""

        test_target = extract_from_query(query, r'(?:test\s+|run\s+)([a-zA-Z0-9_\-\.\/]+(?:test[^\s]*|[^\s]*test\.py))')
        target_str = f" {test_target}" if test_target else ""
        return [f"pytest{flag_str}{target_str}".strip()]

    # 8. PIP_UPGRADE
    if python_cmd == "pip_upgrade":
        if pkg:
            return [f"pip install --upgrade {pkg}"]
        if re.search(r'\b(pip)\b', query, re.IGNORECASE):
            return ["pip install --upgrade pip"]
        if re.search(r'\b(requirements?|-r)\b', query, re.IGNORECASE):
            return ["pip install --upgrade -r requirements.txt"]
        return ["pip install --upgrade pip"]

    # Default fallback
    return ["pip list"]
