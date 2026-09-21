"""Core decision engine — the heart of hey-cli.

Implements the speculative fan-out architecture:
  1. Gather context (files, git, OS) — read from environment, ~30ms
  2. Build ALL TypeSafe questions (routing + sub-cmds + flags + safety)
  3. Single API call — ~100-200ms
  4. Code reads only the answers that match the chosen routing bucket
  5. Build shell command(s) from templates
  6. Display, confirm, execute
"""

from __future__ import annotations

import re
from typing import Any

from typesafe_sdk import Choice, Noul, Score

from hey.command_tree.questions import (
    bucket_question,
    command_count_question,
    flag_questions,
    safety_question,
    sub_command_questions,
)
from hey.context import SystemContext, gather_context
from hey.executor import (
    console,
    display_ambiguous,
    display_command,
    display_error,
    execute_commands,
)
from hey.typesafe_client import ask


# Confidence thresholds for the 3-tier cascade
HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.50
NOUL_THRESHOLD = 0.6


def run(
    query: str,
    auto_yes: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
    no_context: bool = False,
) -> int:
    """Main entry point: natural language query → shell command → execute.

    Returns exit code (0 = success).
    """
    # Step 1: Gather context
    ctx = gather_context(include_git=not no_context)
    if verbose:
        console.print(f"  [dim]Context: {ctx.cwd}, git={ctx.is_git_repo}, "
                       f"files={len(ctx.files)}, os={ctx.os_type}[/dim]")

    # Step 2: Build all questions for speculative fan-out
    questions: dict[str, Choice | Noul | Score] = {}
    questions.update(command_count_question())
    questions.update(bucket_question())
    questions.update(sub_command_questions())
    questions.update(flag_questions(
        branches=ctx.git_branches if ctx.is_git_repo else ["main"],
        files=ctx.files,
    ))
    questions.update(safety_question())

    # Step 3: Single TypeSafe API call
    state = {
        "user_query": query,
        **ctx.to_state_dict(),
    }

    if verbose:
        console.print(f"  [dim]Sending {len(questions)} questions in one API call...[/dim]")

    response = ask(state=state, questions=questions)

    if verbose:
        console.print(f"  [dim]Tokens used: {response.usage.input_tokens} input[/dim]")

    # Step 4: Read routing answers
    bucket_answer = response.choices["bucket"]
    bucket = bucket_answer.choice
    confidence = bucket_answer.confidence

    if verbose:
        console.print(f"  [dim]Bucket: {bucket} (conf={confidence:.2f})[/dim]")
        # Show top-3 bucket probabilities
        sorted_probs = sorted(
            bucket_answer.probabilities.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        for name, prob in sorted_probs:
            console.print(f"    [dim]{name}: {prob:.2%}[/dim]")

    # 3-Tier confidence cascade
    if confidence < MEDIUM_CONFIDENCE:
        # Low confidence: show top interpretations
        sorted_probs = sorted(
            bucket_answer.probabilities.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        chosen = display_ambiguous(query, sorted_probs)
        if chosen is None:
            display_error("Could not determine what you want. Try rephrasing.")
            return 1
        bucket = chosen

    elif confidence < HIGH_CONFIDENCE:
        # Medium confidence: proceed but note uncertainty
        if verbose:
            console.print(f"  [yellow]Medium confidence ({confidence:.0%}) — proceeding with best guess[/yellow]")

    # Step 5: Read sub-command and build command(s)
    cmd_count_answer = response.choices["command_count"]
    cmd_count = cmd_count_answer.choice

    # Determine how many commands
    if cmd_count == "one":
        num_commands = 1
    elif cmd_count == "two":
        num_commands = 2
    else:
        num_commands = 3  # cap at 3 for safety

    # Build command(s) using the appropriate bucket builder
    commands = _build_commands(bucket, response, ctx, query, num_commands)

    if not commands:
        display_error(f"Could not build a command for bucket '{bucket}'. Try being more specific.")
        return 1

    # Step 6: Safety check
    risk_score = response.scores["destructive_risk"].score

    # Step 7: Display and confirm
    confirmed = display_command(
        commands=commands,
        confidence=confidence,
        risk_score=risk_score,
        dry_run=dry_run,
        auto_yes=auto_yes,
        verbose_info=f"bucket={bucket}, cmd_count={cmd_count}" if verbose else "",
    )

    if not confirmed:
        if not dry_run:
            console.print("  [dim]Cancelled.[/dim]")
        return 0

    # Step 8: Execute
    return execute_commands(commands)


def _build_commands(
    bucket: str,
    response: Any,
    ctx: SystemContext,
    query: str,
    num_commands: int,
) -> list[str]:
    """Build shell command(s) using the bucket-specific builder.

    For multi-command scenarios, we build up to ``num_commands`` from a
    single response when possible (e.g., "commit and push" → 3 commands
    from one API call).
    """
    # Import the right bucket builder
    builder = _get_bucket_builder(bucket)
    if builder is None:
        return []

    # Build a context dict the bucket builders can use
    context_dict = ctx.to_state_dict()
    context_dict["query"] = query
    context_dict["user_query"] = query

    try:
        commands = builder(response, context_dict)
    except Exception:
        return []

    # For multi-command, try to generate the full pipeline
    if num_commands > 1 and len(commands) == 1:
        commands = _expand_multi_command(bucket, response, ctx, query, commands, num_commands)

    return commands[:num_commands]


def _get_bucket_builder(bucket: str):
    """Return the build function for a bucket, or None."""
    try:
        if bucket == "git":
            from hey.command_tree.buckets.git import build
        elif bucket == "file":
            from hey.command_tree.buckets.file_ops import build
        elif bucket == "docker":
            from hey.command_tree.buckets.docker import build
        elif bucket == "npm":
            from hey.command_tree.buckets.npm_yarn import build
        elif bucket == "python":
            from hey.command_tree.buckets.python_env import build
        elif bucket == "system":
            from hey.command_tree.buckets.system import build
        elif bucket == "network":
            from hey.command_tree.buckets.network import build
        elif bucket == "search":
            from hey.command_tree.buckets.search import build
        elif bucket == "compress":
            from hey.command_tree.buckets.compress import build
        else:
            return None
        return build
    except ImportError:
        return None


def _expand_multi_command(
    bucket: str,
    response: Any,
    ctx: SystemContext,
    query: str,
    first_commands: list[str],
    num_commands: int,
) -> list[str]:
    """Expand a single-command result into a multi-command pipeline.

    Common patterns like "commit and push" are handled as templates.
    """
    commands = list(first_commands)

    # Handle common multi-command git patterns
    if bucket == "git":
        cmd = response.choices["git_cmd"].choice

        # "add and commit" or "commit and push" or "add, commit, push"
        query_lower = query.lower()

        if "commit" in query_lower and "push" in query_lower:
            # Full add → commit → push pipeline
            from hey.context import generate_commit_message
            msg = generate_commit_message()

            if response.nouls["git_commit_all"].noul > NOUL_THRESHOLD:
                stage_cmd = "git add ."
            else:
                stage_cmd = "git add ."  # default to all

            branch = ctx.git_branch or "main"
            try:
                branch = response.choices["git_target_branch"].choice
            except (KeyError, AttributeError):
                pass

            force = "--force " if response.nouls["git_force"].noul > NOUL_THRESHOLD else ""

            commands = [
                stage_cmd,
                f'git commit -m "{msg}"',
                f"git push {force}origin {branch}".strip(),
            ]

        elif "add" in query_lower and "commit" in query_lower:
            from hey.context import generate_commit_message
            msg = generate_commit_message()
            commands = [
                "git add .",
                f'git commit -m "{msg}"',
            ]

        elif cmd == "push" and "add" not in query_lower:
            # Just push — already handled as single command
            pass

    return commands[:num_commands]


def extract_from_query(query: str, pattern: str) -> str | None:
    """Extract a match from the user query using a regex pattern."""
    match = re.search(pattern, query, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_url(query: str) -> str | None:
    """Extract a URL from the query."""
    return extract_from_query(query, r'(https?://\S+)')


def extract_package_name(query: str) -> str | None:
    """Try to extract a package name from common install patterns."""
    # "install express" → "express"
    # "add react" → "react"
    # "pip install flask" → "flask"
    patterns = [
        r'(?:install|add|remove|uninstall)\s+(\S+)',
        r'(?:pip|npm|yarn|pnpm)\s+(?:install|add|remove|uninstall)\s+(\S+)',
    ]
    for pat in patterns:
        result = extract_from_query(query, pat)
        if result and not result.startswith("-"):
            return result
    return None


def extract_port(query: str) -> str | None:
    """Extract a port number from the query."""
    return extract_from_query(query, r'(?:port)\s*(\d{2,5})')


def extract_search_pattern(query: str) -> str | None:
    """Extract a search pattern from the query."""
    patterns = [
        r'(?:containing?|with|for|pattern)\s+["\']?([^"\']+)["\']?',
        r'(?:grep|search|find)\s+(?:for\s+)?["\']?([^"\']+?)["\']?\s*(?:in|$)',
    ]
    for pat in patterns:
        result = extract_from_query(query, pat)
        if result:
            return result
    return None
