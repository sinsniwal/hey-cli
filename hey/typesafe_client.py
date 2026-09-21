"""Thin wrapper around the TypeSafe Python SDK."""

from __future__ import annotations

from typing import Any

from typesafe_sdk import (
    Choice,
    Noul,
    Score,
    TypeSafeClient,
)

from hey.config import load_api_key


def ask(
    state: str | dict | list,
    questions: dict[str, Choice | Noul | Score],
) -> Any:
    """Send a single System One request and return the response.

    Uses the synchronous client for simplicity in a CLI tool.
    The response object has:
      - response.choices["key"].choice / .probabilities / .confidence
      - response.scores["key"].score / .legend / .probabilities / .confidence
      - response.nouls["key"].noul  (float 0-1, no confidence field)
      - response.usage.input_tokens
    """
    api_key = load_api_key()
    with TypeSafeClient(api_key=api_key) as client:
        response = client.system_one(state=state, questions=questions)
    return response
