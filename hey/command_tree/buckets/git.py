"""Git command builder for TypeSafe speculative fan-out responses."""

from __future__ import annotations

import re
from typing import Any

from hey.context import generate_commit_message

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
    """Translate TypeSafe response and system context into git shell commands."""
    ctx_dict = context if isinstance(context, dict) else {}
    query = _get_query(context)

    git_cmd = _get_choice(response, "git_cmd", default="status")
    force = _get_noul(response, "git_force")
    set_upstream = _get_noul(response, "git_set_upstream")
    amend = _get_noul(response, "git_amend")
    commit_all = _get_noul(response, "git_commit_all")
    stash_pop = _get_noul(response, "git_stash_pop")

    target_branch = _get_choice(response, "git_target_branch", default="")
    current_branch = str(ctx_dict.get("git_branch", "") or "")

    # Resolve target branch if not chosen
    if not target_branch:
        extracted = extract_from_query(
            query,
            r'(?:branch|to|into|from|checkout|merge|rebase)\s+([a-zA-Z0-9_\-\.\/]+)',
        )
        target_branch = extracted or current_branch or "main"

    # 1. ADD
    if git_cmd == "add":
        target_file = _get_choice(response, "target_file", default="")
        if not target_file:
            target_file = extract_from_query(query, r'(?:add|stage)\s+([^\s]+)') or ""
        if target_file and target_file not in (".", "all", "-A"):
            return [f"git add {target_file}"]
        if commit_all:
            return ["git add -A"]
        return ["git add ."]

    # 2. COMMIT
    if git_cmd == "commit":
        # Extract custom message if in quotes or provided in query
        msg = extract_from_query(query, r'["\']([^"\']+)["\']')
        if not msg:
            msg = extract_from_query(query, r'(?:message|-m)\s+["\']?([^"\'\n]+)["\']?')
        if not msg:
            msg = generate_commit_message()

        # Sanitize double quotes in commit message
        safe_msg = msg.replace('"', '\\"')

        flags: list[str] = []
        if commit_all:
            flags.append("-a")
        if amend:
            flags.append("--amend")

        flag_str = f" {' '.join(flags)}" if flags else ""
        return [f'git commit{flag_str} -m "{safe_msg}"']

    # 3. PUSH
    if git_cmd == "push":
        push_parts = ["git push"]
        if force:
            push_parts.append("--force")
        if set_upstream:
            branch = target_branch or current_branch or "main"
            push_parts.extend(["-u", "origin", branch])
        elif target_branch and target_branch != current_branch:
            push_parts.extend(["origin", target_branch])
        elif force and current_branch:
            push_parts.extend(["origin", current_branch])
        return [" ".join(push_parts)]

    # 4. PULL
    if git_cmd == "pull":
        pull_parts = ["git pull"]
        if re.search(r'\b(rebase)\b', query, re.IGNORECASE):
            pull_parts.append("--rebase")
        if target_branch and target_branch != current_branch:
            pull_parts.extend(["origin", target_branch])
        return [" ".join(pull_parts)]

    # 5. CHECKOUT
    if git_cmd == "checkout":
        new_branch = extract_from_query(
            query,
            r'(?:new|create|-b)\s+(?:branch\s+)?([a-zA-Z0-9_\-\.\/]+)',
        )
        if new_branch:
            return [f"git checkout -b {new_branch}"]
        branch = target_branch or "main"
        return [f"git checkout {branch}"]

    # 6. BRANCH
    if git_cmd == "branch":
        if re.search(r'\b(delete|remove|-d|-D)\b', query, re.IGNORECASE):
            branch_to_del = extract_from_query(
                query,
                r'(?:delete|remove|-d|-D)\s+(?:branch\s+)?([a-zA-Z0-9_\-\.\/]+)',
            ) or target_branch
            flag = "-D" if force else "-d"
            return [f"git branch {flag} {branch_to_del}"]
        new_branch = extract_from_query(
            query,
            r'(?:create|make|new)\s+(?:branch\s+)?([a-zA-Z0-9_\-\.\/]+)',
        )
        if new_branch:
            return [f"git branch {new_branch}"]
        return ["git branch -a"]

    # 7. MERGE
    if git_cmd == "merge":
        branch = target_branch or "main"
        return [f"git merge {branch}"]

    # 8. STASH
    if git_cmd == "stash":
        if stash_pop or re.search(r'\bpop\b', query, re.IGNORECASE):
            return ["git stash pop"]
        if re.search(r'\bapply\b', query, re.IGNORECASE):
            return ["git stash apply"]
        if re.search(r'\blist\b', query, re.IGNORECASE):
            return ["git stash list"]
        if re.search(r'\bdrop\b', query, re.IGNORECASE):
            return ["git stash drop"]
        return ["git stash"]

    # 9. LOG
    if git_cmd == "log":
        if re.search(r'\bgraph\b', query, re.IGNORECASE):
            return ["git log --graph --oneline -n 10"]
        num = extract_from_query(query, r'(?:-n|last)\s*(\d+)')
        n_count = num if num else "10"
        return [f"git log --oneline -n {n_count}"]

    # 10. DIFF
    if git_cmd == "diff":
        if re.search(r'\b(staged|cached)\b', query, re.IGNORECASE):
            return ["git diff --cached"]
        target_file = _get_choice(response, "target_file", default="")
        if target_file:
            return [f"git diff {target_file}"]
        return ["git diff"]

    # 11. RESET
    if git_cmd == "reset":
        if re.search(r'\bhard\b', query, re.IGNORECASE):
            return ["git reset --hard HEAD"]
        if re.search(r'\bsoft\b', query, re.IGNORECASE):
            return ["git reset --soft HEAD~1"]
        target_file = _get_choice(response, "target_file", default="")
        if target_file:
            return [f"git reset {target_file}"]
        return ["git reset HEAD~1"]

    # 12. CLONE
    if git_cmd == "clone":
        url = extract_from_query(
            query,
            r'((?:https?://|git@|gh:)[^\s\'"]+)',
        )
        if not url:
            url = extract_from_query(query, r'clone\s+([^\s\'"]+)')
        if url:
            # Clean trailing punctuation if any
            clean_url = url.rstrip(".,;)")
            return [f"git clone {clean_url}"]
        return ["git clone <repo-url>"]

    # 13. STATUS
    if git_cmd == "status":
        if re.search(r'\b(short|-s)\b', query, re.IGNORECASE):
            return ["git status -s"]
        return ["git status"]

    # 14. REBASE
    if git_cmd == "rebase":
        if re.search(r'\bcontinue\b', query, re.IGNORECASE):
            return ["git rebase --continue"]
        if re.search(r'\babort\b', query, re.IGNORECASE):
            return ["git rebase --abort"]
        branch = target_branch or "main"
        return [f"git rebase {branch}"]

    # 15. TAG
    if git_cmd == "tag":
        tag_name = extract_from_query(
            query,
            r'(?:tag|version|release)\s+([vV]?[0-9]+(?:\.[0-9]+)*(?:-[a-zA-Z0-9\.]+)?)',
        )
        if tag_name:
            return [f"git tag {tag_name}"]
        return ["git tag -l"]

    # Sensible default
    return ["git status"]
