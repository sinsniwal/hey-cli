import argparse
import sys
import os
import urllib.request
import urllib.error

from .governance import GovernanceEngine
from .llm import generate_command
from .history import HistoryManager
from .runner import CommandRunner
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def check_ollama():
    """Check if Ollama is reachable. Exit with instructions if not."""
    from .llm import OLLAMA_HOST

    try:
        urllib.request.urlopen(OLLAMA_HOST, timeout=2)
    except Exception:
        msg = Text()
        msg.append("Ollama is not running or not installed.\n\n", style="bold red")
        msg.append("1. Install Ollama:\n", style="bold white")
        msg.append("   Linux / macOS:\n", style="dim")
        msg.append(
            "     curl -fsSL https://ollama.com/install.sh | sh\n", style="bold cyan"
        )
        msg.append("   Windows:\n", style="dim")
        msg.append("     https://ollama.com/download/windows\n\n", style="bold cyan")
        msg.append("2. Authenticate:\n", style="bold white")
        msg.append("     ollama login\n\n", style="bold cyan")
        msg.append("3. Pull the default model:\n", style="bold white")
        msg.append("     ollama pull gpt-oss:20b-cloud", style="bold cyan")
        console.print(
            Panel(
                msg,
                title="[bold yellow]⚠  Ollama Required[/bold yellow]",
                border_style="yellow",
            )
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="hey-cli: a secure, zero-bloat CLI companion.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("objective", nargs="*", help="Goal or task description")
    parser.add_argument(
        "--level",
        type=int,
        choices=[0, 1, 2, 3],
        default=None,
        help="0: Dry-Run\n1: Supervised (Default)\n2: Unrestricted (Danger)\n3: Troubleshooter",
    )
    parser.add_argument(
        "--init", action="store_true", help="Initialize ~/.hey-rules.json"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear conversational memory history"
    )
    parser.add_argument(
        "--check-cache", type=str, help="Check local cache for instant fix"
    )
    parser.add_argument(
        "--shell-init", action="store_true", help="Output shell function for directory persistence"
    )

    args = parser.parse_args()

    gov = GovernanceEngine()
    history_mgr = HistoryManager()

    if args.clear:
        history_mgr.clear()
        console.print("[dim]Conversational history wiped clean.[/dim]")
        sys.exit(0)

    active_level = args.level
    if active_level is None:
        active_level = gov.rules.get("config", {}).get("default_level", 1)

    model_name = gov.rules.get("config", {}).get("model", "gpt-oss:20b-cloud")

    if args.init:
        if gov.init_rules():
            console.print(f"Initialized security rules at {gov.rules_path}")
        else:
            console.print(f"Rules already exist at {gov.rules_path}")
        sys.exit(0)

    if args.check_cache:
        sys.exit(0)

    if args.shell_init:
        is_windows = os.name == "nt"
        if is_windows:
            shell_func = r"""
function hey {
    & hey.exe @args
    $handoff = Join-Path $HOME ".hey_cwd_handoff"
    if (Test-Path $handoff) {
        $target = Get-Content $handoff -Raw
        Remove-Item $handoff
        if (Test-Path $target.Trim()) {
            Set-Location $target.Trim()
        }
    }
}
"""
        else:
            shell_func = r"""
hey() {
    command hey "$@"
    if [ -f "$HOME/.hey_cwd_handoff" ]; then
        local target=$(cat "$HOME/.hey_cwd_handoff")
        rm -f "$HOME/.hey_cwd_handoff"
        [ -d "$target" ] && cd "$target"
    fi
}
"""
        print(shell_func.strip())
        sys.exit(0)

    # Only check Ollama when we're about to call the LLM
    check_ollama()

    piped_data = ""
    if not sys.stdin.isatty():
        try:
            piped_data = sys.stdin.read()
            sys.stdin = open("/dev/tty")
        except Exception:
            pass

    objective = " ".join(args.objective).strip()
    if not objective and not piped_data:
        parser.print_help()
        sys.exit(1)

    # Build complete user message for saving later
    user_prompt = objective
    if piped_data:
        user_prompt += f"\n\n[Piped Data]:\n{piped_data}"

    console.print("[bold yellow]●[/bold yellow] Thinking...")
    past_messages = history_mgr.load()
    try:
        response = generate_command(
            objective, context=piped_data, model_name=model_name, history=past_messages
        )
    except urllib.error.HTTPError as e:
        if e.code == 401:
            msg = Text()
            msg.append("Ollama authentication required.\n\n", style="bold red")
            msg.append("Your connection to Ollama is not authenticated.\n", style="bold white")
            msg.append("\nPlease run: ", style="dim")
            msg.append("ollama login\n", style="bold cyan")
            msg.append("\nThis will verify your identity with Ollama and allow the request to proceed.", style="dim")
            console.print(Panel(msg, title="[bold yellow]🔑 Authentication Required[/bold yellow]", border_style="yellow"))
        else:
            console.print(f"\n[bold red]● Ollama API error:[/bold red] HTTP {e.code} — {e.reason}")
        sys.exit(1)
    except (urllib.error.URLError, ConnectionError, OSError):
        check_ollama()  # shows the panel and exits
        sys.exit(1)  # fallback — should never reach here
    except Exception as e:
        console.print(f"\n[bold red]● Error:[/bold red] {e}")
        sys.exit(1)

    # Save the user query to history IMMEDIATELY
    history_mgr.append("user", user_prompt)

    runner = CommandRunner(
        governance=gov,
        level=active_level,
        model_name=model_name,
        history_mgr=history_mgr,
    )
    runner.execute_flow(response, objective)


if __name__ == "__main__":
    main()
