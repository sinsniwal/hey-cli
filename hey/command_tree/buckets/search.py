"""Search and text processing command builder for TypeSafe speculative fan-out responses."""

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


def _extract_search_pattern(query: str) -> str | None:
    """Extract search pattern from quotes or standard keywords."""
    quoted = extract_from_query(query, r'["\']([^"\']+)["\']')
    if quoted:
        return quoted

    after_kw = extract_from_query(
        query,
        r'(?:grep|search(?:\s+for)?|find(?:\s+all)?|matching|pattern)\s+([a-zA-Z0-9_\-\.\*\?]+)',
    )
    if after_kw and after_kw.lower() not in ("all", "files", "lines", "words", "text", "in", "directory"):
        return after_kw
    return None


def build(response: Any, context: dict[str, Any] | Any) -> list[str]:
    """Translate TypeSafe response and system context into search/text processing shell commands."""
    ctx_dict = context if isinstance(context, dict) else {}
    query = _get_query(context)
    os_type = str(ctx_dict.get("os_type", "")).lower()

    search_cmd = _get_choice(response, "search_cmd", default="grep")
    recursive = _get_noul(response, "search_recursive")
    case_insensitive = _get_noul(response, "search_case_insensitive")
    count_only = _get_noul(response, "search_count_only")
    target_file = _get_choice(response, "target_file", default="")

    pattern = _extract_search_pattern(query)

    # 1. GREP
    if search_cmd == "grep":
        flags: list[str] = []
        if recursive:
            flags.append("r")
            flags.append("n")  # include line numbers for recursive grep
        if case_insensitive or re.search(r'\b(case[- ]insensitive|ignore[- ]case|-i)\b', query, re.IGNORECASE):
            flags.append("i")
        if count_only or re.search(r'\b(count|how many|-c)\b', query, re.IGNORECASE):
            flags.append("c")

        # Deduplicate flag chars while preserving order
        seen_flags: set[str] = set()
        flag_chars: list[str] = []
        for ch in flags:
            if ch not in seen_flags:
                seen_flags.add(ch)
                flag_chars.append(ch)

        flag_str = f"-{''.join(flag_chars)}" if flag_chars else "-n"
        search_target = target_file or ("." if "r" in flag_chars else "*")
        search_pat = pattern or "<pattern>"

        return [f'grep {flag_str} "{search_pat}" {search_target}']

    # 2. FIND
    if search_cmd == "find":
        find_name = pattern
        if not find_name or find_name.lower() in ("files", "file", "all"):
            name_match = extract_from_query(
                query,
                r'(?:files?\s+(?:named?|matching|with)\s+|named?\s+|matching\s+|pattern\s+)["\']?([a-zA-Z0-9_\-\.\*\?]+)["\']?',
            )
            if not name_match:
                name_match = extract_from_query(
                    query,
                    r'find\s+(?:all\s+)?(?:files?\s+)?(?:in\s+[^\s]+\s+)?["\']?([a-zA-Z0-9_\-\.\*\?]+)["\']?',
                )
            find_name = name_match or "*"

        if find_name and find_name.lower() in ("files", "file", "named", "name", "all"):
            find_name = "*"

        if not any(c in find_name for c in ("*", "?", ".")):
            find_name = f"*{find_name}*"

        name_opt = "-iname" if case_insensitive else "-name"
        type_opt = ""
        if re.search(r'\b(directories|folders?|dirs?)\b', query, re.IGNORECASE):
            type_opt = " -type d"
        elif re.search(r'\b(files?)\b', query, re.IGNORECASE):
            type_opt = " -type f"

        dir_target = target_file if target_file and not target_file.endswith((".py", ".txt", ".js", ".json", ".md")) else "."
        return [f'find {dir_target}{type_opt} {name_opt} "{find_name}"']

    # 3. SED
    if search_cmd == "sed":
        sed_expr = extract_from_query(query, r'["\'](s/[^"\']+)["\']')
        if not sed_expr:
            sub_match = re.search(r'replace\s+([^\s]+)\s+with\s+([^\s]+)', query, re.IGNORECASE)
            if sub_match:
                old_val, new_val = sub_match.group(1), sub_match.group(2)
                sed_expr = f"s/{old_val}/{new_val}/g"
            else:
                sed_expr = "s/old/new/g"

        target = target_file or extract_from_query(query, r'(?:in|file)\s+([^\s]+)') or "<file>"

        # macOS / BSD sed requires an empty string for the backup extension with -i
        if "darwin" in os_type or "mac" in os_type:
            return [f"sed -i '' '{sed_expr}' {target}"]
        return [f"sed -i '{sed_expr}' {target}"]

    # 4. AWK
    if search_cmd == "awk":
        awk_expr = extract_from_query(query, r'["\']({[^"\']+})["\']')
        if not awk_expr:
            col_match = extract_from_query(query, r'(?:column|col|field)\s*(\d+)')
            if col_match:
                awk_expr = f"{{print ${col_match}}}"
            else:
                awk_expr = "{print $1}"

        target = target_file or extract_from_query(query, r'(?:in|from|file)\s+([a-zA-Z0-9_\-\.\/]+)') or "<file>"
        return [f"awk '{awk_expr}' {target}"]

    # 5. SORT
    if search_cmd == "sort":
        flags: list[str] = []
        if re.search(r'\b(unique|dedup|duplicate|-u)\b', query, re.IGNORECASE):
            flags.append("-u")
        if re.search(r'\b(reverse|descending|-r)\b', query, re.IGNORECASE):
            flags.append("-r")
        if re.search(r'\b(numeric|numbers|-n)\b', query, re.IGNORECASE):
            flags.append("-n")

        target = target_file or extract_from_query(
            query,
            r'(?:sort\s+(?:unique\s+|numeric\s+|reverse\s+|-u\s+|-n\s+|-r\s+)?|in\s+|file\s+)([a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+|[a-zA-Z0-9_\-\.\/]+)',
        )
        if not target or target.lower() in ("unique", "reverse", "numeric", "file", "all"):
            target = "<file>"

        flag_str = f" {' '.join(flags)}" if flags else ""
        return [f"sort{flag_str} {target}"]

    # 6. XARGS
    if search_cmd == "xargs":
        action = extract_from_query(query, r'xargs\s+(.+)')
        if not action:
            action_verb = extract_from_query(query, r'(?:and|then)\s+(rm|delete|kill|cat|mv|cp)')
            action = action_verb if action_verb else "rm"
        return [f"xargs {action}"]

    # 7. WC
    if search_cmd == "wc":
        target = target_file or extract_from_query(query, r'(?:in|for|file)\s+([^\s]+)') or "*"
        if count_only or re.search(r'\b(lines?|-l)\b', query, re.IGNORECASE):
            return [f"wc -l {target}"]
        if re.search(r'\b(words?|-w)\b', query, re.IGNORECASE):
            return [f"wc -w {target}"]
        if re.search(r'\b(chars?|bytes?|-c|-m)\b', query, re.IGNORECASE):
            return [f"wc -c {target}"]
        return [f"wc -l {target}"]

    # Default fallback
    search_pat = pattern or "<pattern>"
    return [f'grep -rn "{search_pat}" .']
