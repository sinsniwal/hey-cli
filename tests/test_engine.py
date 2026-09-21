"""Integration tests for hey-cli using TypeSafe to score results.

The user's insight: use TypeSafe itself to judge whether the generated
command is correct.  We send the original query + generated command to
TypeSafe and ask "Is this the right command?" — a Noul question that
returns a calibrated probability.

Run with:
    python -m pytest tests/test_engine.py -v -m integration
"""

from __future__ import annotations

import os
import sys
import pytest

# Skip all tests if no API key available
pytestmark = pytest.mark.integration
SKIP_REASON = "TYPESAFE_API_KEY not set"


def has_api_key() -> bool:
    # Try loading from .env in project root
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
    return bool(os.environ.get("TYPESAFE_API_KEY"))


def score_command(query: str, generated_command: str) -> float:
    """Ask TypeSafe: 'Is this the right command for the query?'

    Returns a probability (0-1) that the command is correct.
    This is the meta-test — TypeSafe judging its own output.
    """
    from typesafe_sdk import Noul
    from hey.typesafe_client import ask

    response = ask(
        state={
            "user_query": query,
            "generated_command": generated_command,
        },
        questions={
            "is_correct": Noul(
                instructions=(
                    "The generated shell command correctly accomplishes "
                    "the task described in the user query"
                ),
                criteria={
                    "true": (
                        "The command uses the right tool, correct flags, "
                        "and would produce the expected result on a standard "
                        "Unix/macOS/Linux system"
                    ),
                    "false": (
                        "The command is wrong, uses incorrect flags, would "
                        "fail, or does something different from what was asked"
                    ),
                },
            ),
            "is_safe": Noul(
                instructions=(
                    "The generated command is safe to run and will not cause "
                    "data loss or irreversible damage beyond what was requested"
                ),
            ),
        },
    )

    return response.nouls["is_correct"].noul


# ---------------------------------------------------------------------------
# Test cases: (query, expected_substring, description)
# ---------------------------------------------------------------------------

TEST_CASES = [
    # --- Git ---
    ("show the git log", "git log", "Basic git log"),
    ("push to main", "git push", "Git push to main"),
    ("check git status", "git status", "Git status"),
    ("create a new branch called feature", "git branch", "Git branch create"),
    ("stash my changes", "git stash", "Git stash"),

    # --- File operations ---
    ("create a directory called src", "mkdir", "Create directory"),
    ("list files in current directory", "ls", "List files"),

    # --- Search ---
    ("find all python files", "find", "Find python files"),

    # --- System ---
    ("show disk usage", "d", "Disk usage (df or du)"),
    ("what is my username", "whoami", "Whoami"),

    # --- Docker ---
    ("list running docker containers", "docker ps", "Docker ps"),

    # --- Network ---
    ("ping google.com", "ping", "Ping"),

    # --- Compress ---
    ("extract archive.tar.gz", "tar", "Tar extract"),

    # --- npm ---
    ("install express", "install", "npm install"),

    # --- Python ---
    ("run the tests", "pytest", "Run pytest"),
]


@pytest.mark.skipif(not has_api_key(), reason=SKIP_REASON)
@pytest.mark.parametrize(
    "query, expected_substr, description",
    TEST_CASES,
    ids=[tc[2] for tc in TEST_CASES],
)
def test_command_generation(query: str, expected_substr: str, description: str):
    """Test that hey-cli generates a reasonable command, scored by TypeSafe."""
    from hey.context import gather_context
    from hey.engine import run as _run_engine
    from hey.command_tree.questions import (
        bucket_question,
        command_count_question,
        flag_questions,
        safety_question,
        sub_command_questions,
    )
    from hey.typesafe_client import ask as ts_ask
    from typesafe_sdk import Choice, Noul, Score

    # Gather minimal context
    ctx = gather_context(include_git=True)

    # Build questions
    questions: dict[str, Choice | Noul | Score] = {}
    questions.update(command_count_question())
    questions.update(bucket_question())
    questions.update(sub_command_questions())
    questions.update(flag_questions(
        branches=ctx.git_branches if ctx.is_git_repo else ["main"],
        files=ctx.files,
    ))
    questions.update(safety_question())

    state = {"user_query": query, **ctx.to_state_dict()}
    response = ts_ask(state=state, questions=questions)

    # Get bucket and build command
    bucket = response.choices["bucket"].choice

    from hey.engine import _build_commands
    commands = _build_commands(bucket, response, ctx, query, num_commands=1)

    assert commands, f"No commands generated for: {query}"

    full_command = " && ".join(commands)

    # Basic substring check
    assert expected_substr.lower() in full_command.lower(), (
        f"Expected '{expected_substr}' in '{full_command}' for: {description}"
    )

    # Meta-test: ask TypeSafe if this is correct
    correctness_score = score_command(query, full_command)

    print(f"\n  [{description}]")
    print(f"    Query:     {query}")
    print(f"    Command:   {full_command}")
    print(f"    Correct:   {correctness_score:.2%}")

    # Pass if TypeSafe says > 60% likely correct
    assert correctness_score > 0.60, (
        f"TypeSafe scored '{full_command}' at {correctness_score:.2%} "
        f"for query '{query}' — below 60% threshold"
    )


@pytest.mark.skipif(not has_api_key(), reason=SKIP_REASON)
def test_destructive_command_has_high_risk():
    """Verify that destructive commands get high risk scores."""
    from hey.context import gather_context
    from hey.command_tree.questions import (
        bucket_question,
        command_count_question,
        flag_questions,
        safety_question,
        sub_command_questions,
    )
    from hey.typesafe_client import ask as ts_ask
    from typesafe_sdk import Choice, Noul, Score

    ctx = gather_context(include_git=False)

    questions: dict[str, Choice | Noul | Score] = {}
    questions.update(command_count_question())
    questions.update(bucket_question())
    questions.update(sub_command_questions())
    questions.update(flag_questions(branches=["main"], files=ctx.files))
    questions.update(safety_question())

    response = ts_ask(
        state={"user_query": "delete everything in the current directory", **ctx.to_state_dict()},
        questions=questions,
    )

    risk = response.scores["destructive_risk"].score
    print(f"\n  Risk score for 'delete everything': {risk:.2f}")
    assert risk >= 1.5, f"Expected high risk score, got {risk:.2f}"


@pytest.mark.skipif(not has_api_key(), reason=SKIP_REASON)
def test_multi_command_commit_and_push():
    """Verify that 'commit and push' generates multiple commands."""
    from hey.context import gather_context
    from hey.command_tree.questions import (
        bucket_question,
        command_count_question,
        flag_questions,
        safety_question,
        sub_command_questions,
    )
    from hey.typesafe_client import ask as ts_ask
    from typesafe_sdk import Choice, Noul, Score

    ctx = gather_context(include_git=True)

    questions: dict[str, Choice | Noul | Score] = {}
    questions.update(command_count_question())
    questions.update(bucket_question())
    questions.update(sub_command_questions())
    questions.update(flag_questions(
        branches=ctx.git_branches if ctx.is_git_repo else ["main"],
        files=ctx.files,
    ))
    questions.update(safety_question())

    state = {"user_query": "commit everything and push to main", **ctx.to_state_dict()}
    response = ts_ask(state=state, questions=questions)

    cmd_count = response.choices["command_count"].choice
    print(f"\n  Command count for 'commit and push': {cmd_count}")

    # Should be multi-command
    assert cmd_count in ("two", "three_plus"), (
        f"Expected multi-command, got '{cmd_count}'"
    )

    bucket = response.choices["bucket"].choice
    assert bucket == "git", f"Expected git bucket, got '{bucket}'"
