"""Compression and archive command builder for TypeSafe speculative fan-out responses."""

from __future__ import annotations

import re
from pathlib import Path
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
    """Translate TypeSafe response and system context into compression shell commands."""
    query = _get_query(context)

    compress_cmd = _get_choice(response, "compress_cmd", default="tar_create")
    target_file = _get_choice(response, "target_file", default="")

    # 1. TAR_CREATE
    if compress_cmd == "tar_create":
        archive = extract_from_query(query, r'([a-zA-Z0-9_\-\.]+\.(?:tar\.gz|tgz|tar))')
        target = target_file or extract_from_query(
            query,
            r'(?:tar|compress|archive)\s+(?:directory\s+|folder\s+)?([^\s]+)',
        ) or "."

        if not archive:
            base_name = Path(target).stem if target != "." else "archive"
            archive = f"{base_name}.tar.gz"

        return [f"tar -czvf {archive} {target}"]

    # 2. TAR_EXTRACT
    if compress_cmd == "tar_extract":
        archive = extract_from_query(query, r'([a-zA-Z0-9_\-\.]+\.(?:tar\.gz|tgz|tar))')
        if not archive:
            if target_file and any(target_file.endswith(ext) for ext in (".tar.gz", ".tgz", ".tar")):
                archive = target_file
        archive = archive or target_file or "archive.tar.gz"

        flags = "-xzvf" if archive.endswith((".tar.gz", ".tgz")) else "-xvf"
        return [f"tar {flags} {archive}"]

    # 3. ZIP_CREATE
    if compress_cmd == "zip_create":
        archive = extract_from_query(query, r'([a-zA-Z0-9_\-\.]+\.zip)')
        target = target_file or extract_from_query(
            query,
            r'(?:zip|compress)\s+(?:directory\s+|folder\s+)?([^\s]+)',
        ) or "."

        if not archive:
            base_name = Path(target).stem if target != "." else "archive"
            archive = f"{base_name}.zip"

        return [f"zip -r {archive} {target}"]

    # 4. ZIP_EXTRACT
    if compress_cmd == "zip_extract":
        archive = extract_from_query(query, r'([a-zA-Z0-9_\-\.]+\.zip)')
        if not archive and target_file and target_file.endswith(".zip"):
            archive = target_file
        archive = archive or target_file or "archive.zip"
        return [f"unzip {archive}"]

    # 5. GZIP
    if compress_cmd == "gzip":
        target = target_file or extract_from_query(
            query,
            r'(?:gzip|compress)\s+([^\s]+)',
        ) or "<file>"

        flag = " -k" if re.search(r'\b(keep|original|-k)\b', query, re.IGNORECASE) else ""
        return [f"gzip{flag} {target}"]

    # 6. GUNZIP
    if compress_cmd == "gunzip":
        target = target_file or extract_from_query(
            query,
            r'(?:gunzip|decompress|uncompress)\s+([^\s]+)',
        )
        if not target and target_file:
            target = target_file
        target = target or "<file.gz>"
        return [f"gunzip {target}"]

    # Default fallback
    return ["tar -czvf archive.tar.gz ."]
