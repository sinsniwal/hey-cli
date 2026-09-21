"""Safe command execution with rich terminal display."""

from __future__ import annotations

import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


console = Console()


def display_command(
    commands: list[str],
    confidence: float,
    risk_score: float,
    dry_run: bool = False,
    auto_yes: bool = False,
    verbose_info: str = "",
) -> bool:
    """Show the resolved command(s) and ask for confirmation.

    Returns True if the user confirms execution.
    """
    # Build the command display
    lines: list[str] = []
    for i, cmd in enumerate(commands):
        prefix = f"  {i + 1}. " if len(commands) > 1 else "  $ "
        lines.append(prefix + cmd)

    cmd_text = "\n".join(lines)

    # Confidence line
    conf_pct = f"{confidence * 100:.0f}%"

    # Risk assessment
    if risk_score >= 2.0:
        risk_label = "[bold red]⚠️  DANGEROUS — irreversible operation[/bold red]"
    elif risk_score >= 1.0:
        risk_label = "[yellow]⚡ Moderate — non-idempotent write[/yellow]"
    else:
        risk_label = "[green]✓ Safe — read-only or idempotent[/green]"

    # Build panel content
    content_parts = [
        f"[bold cyan]{cmd_text}[/bold cyan]",
        "",
        f"  Confidence: [bold]{conf_pct}[/bold]",
        f"  Risk: {risk_label}",
    ]

    if verbose_info:
        content_parts.extend(["", f"  [dim]{verbose_info}[/dim]"])

    if dry_run:
        content_parts.extend(["", "  [dim italic]--dry-run: command will NOT be executed[/dim italic]"])

    panel_content = "\n".join(content_parts)

    title = "hey-cli" if len(commands) == 1 else f"hey-cli ({len(commands)} commands)"
    console.print(Panel(panel_content, title=title, border_style="bright_blue"))

    if dry_run:
        return False

    if auto_yes:
        console.print("  [dim]--yes: auto-confirmed[/dim]")
        return True

    if risk_score < 1.0:
        console.print("  [dim]Auto-executing safe command...[/dim]")
        return True

    # Confirmation prompt
    if risk_score >= 2.0:
        prompt_text = "  [bold red]Execute dangerous command? Type 'yes' to confirm:[/bold red] "
        console.print(prompt_text, end="")
        answer = input().strip().lower()
        return answer == "yes"
    else:
        console.print("  Execute? [Y/n] ", end="")
        answer = input().strip().lower()
        return answer in ("", "y", "yes")


def execute_commands(commands: list[str]) -> int:
    """Execute a list of shell commands sequentially.

    Returns the exit code of the last command (0 = success).
    """
    for i, cmd in enumerate(commands):
        if len(commands) > 1:
            console.print(f"\n  [dim]Running ({i + 1}/{len(commands)}):[/dim] [cyan]{cmd}[/cyan]")
        else:
            console.print(f"\n  [dim]Running:[/dim] [cyan]{cmd}[/cyan]")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=None,  # use current directory
            )
            if result.returncode != 0:
                console.print(
                    f"\n  [red]✗ Command exited with code {result.returncode}[/red]"
                )
                if i < len(commands) - 1:
                    console.print("  [red]Aborting remaining commands.[/red]")
                return result.returncode
        except KeyboardInterrupt:
            console.print("\n  [yellow]Interrupted by user.[/yellow]")
            return 130
        except Exception as exc:
            console.print(f"\n  [red]✗ Error: {exc}[/red]")
            return 1

    console.print("\n  [green]✓ Done[/green]")
    return 0


def display_error(message: str) -> None:
    """Display an error message."""
    console.print(f"\n  [red]✗ {message}[/red]\n")


def display_ambiguous(
    query: str,
    top_options: list[tuple[str, float]],
) -> str | None:
    """Show top interpretations and let the user pick.

    ``top_options`` is a list of (label, probability) tuples.
    Returns the chosen label, or None if the user cancels.
    """
    console.print(f"\n  [yellow]I'm not confident about:[/yellow] \"{query}\"\n")
    console.print("  Did you mean:\n")

    for i, (label, prob) in enumerate(top_options, 1):
        pct = f"{prob * 100:.0f}%"
        console.print(f"    {i}. {label}  [dim]({pct})[/dim]")

    console.print(f"    {len(top_options) + 1}. [dim]None of these / rephrase[/dim]")
    console.print("\n  Pick a number: ", end="")

    try:
        choice = input().strip()
        idx = int(choice) - 1
        if 0 <= idx < len(top_options):
            return top_options[idx][0]
    except (ValueError, KeyboardInterrupt, EOFError):
        pass

    return None
