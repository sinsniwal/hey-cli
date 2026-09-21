"""Configuration loader: API key and OS detection from environment."""

from __future__ import annotations

import os
import platform
from pathlib import Path

from dotenv import load_dotenv


def _find_dotenv() -> Path | None:
    """Walk up from CWD and package dir to find a .env file."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def load_api_key() -> str:
    """Load TYPESAFE_API_KEY from environment or .env file.

    Raises ``SystemExit`` with a helpful message when the key is missing.
    """
    dotenv_path = _find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path)

    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        raise SystemExit(
            "[hey-cli] TYPESAFE_API_KEY not found.\n"
            "Set it in your environment or create a .env file:\n"
            "  export TYPESAFE_API_KEY=your_key_here\n"
            "  # or\n"
            "  echo 'TYPESAFE_API_KEY=your_key_here' > .env"
        )
    return key


def detect_os() -> str:
    """Detect the operating system.  No API call needed — read from env."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def detect_shell() -> str:
    """Detect the current shell from $SHELL or default."""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    elif "fish" in shell:
        return "fish"
    # Windows
    comspec = os.environ.get("COMSPEC", "")
    if "cmd" in comspec.lower():
        return "cmd"
    if "powershell" in comspec.lower() or os.environ.get("PSModulePath"):
        return "powershell"
    return "sh"
