import argparse
import sys
import os

from .governance import GovernanceEngine
from .llm import generate_command
from .history import HistoryManager
from .runner import CommandRunner
from rich.console import Console

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="hey-cli: a secure, zero-bloat CLI companion.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("objective", nargs="*", help="Goal or task description")
    parser.add_argument("--level", type=int, choices=[0, 1, 2, 3], default=None,
                        help="0: Dry-Run\n1: Supervised (Default)\n2: Unrestricted (Danger)\n3: Troubleshooter")
    parser.add_argument("--init", action="store_true", help="Initialize ~/.hey-rules.json")
    parser.add_argument("--clear", action="store_true", help="Clear conversational memory history")
    parser.add_argument("--check-cache", type=str, help="Check local cache for instant fix")
    
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

    piped_data = ""
    if not sys.stdin.isatty():
        try:
            piped_data = sys.stdin.read()
            sys.stdin = open('/dev/tty')
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
    response = generate_command(objective, context=piped_data, model_name=model_name, history=past_messages)
    
    # Save the user query to history IMMEDIATELY
    history_mgr.append("user", user_prompt)
    
    runner = CommandRunner(governance=gov, level=active_level, model_name=model_name, history_mgr=history_mgr)
    runner.execute_flow(response, objective)

if __name__ == "__main__":
    main()
