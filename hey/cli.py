"""CLI entry point for hey-cli."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from hey import __version__


console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hey",
        description="Natural language → shell commands (powered by TypeSafe AI)",
        epilog="Examples:\n"
        '  hey push to main\n'
        '  hey find all python files\n'
        '  hey stop docker containers --dry-run\n',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "query",
        nargs="+",
        help="Natural language description of what you want to do",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the command without executing it",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show TypeSafe API details (questions, probabilities, tokens)",
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Skip gathering system context (faster, less accurate)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"hey-cli {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    query = " ".join(args.query)
    if not query.strip():
        parser.print_help()
        sys.exit(1)

    # Import here to defer heavy imports until needed
    from hey.engine import run

    try:
        exit_code = run(
            query=query,
            auto_yes=args.yes,
            dry_run=args.dry_run,
            verbose=args.verbose,
            no_context=args.no_context,
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n  [yellow]Interrupted.[/yellow]")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as exc:
        console.print(f"\n  [red]✗ Unexpected error: {exc}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
