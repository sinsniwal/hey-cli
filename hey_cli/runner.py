import subprocess
import sys
import json
import dataclasses
import os
import platform
import re
from typing import Optional

from .governance import GovernanceEngine, Action
from .llm import CommandResponse, TroubleshootResponse, generate_troubleshoot_step, generate_command
from rich.console import Console
from rich.markdown import Markdown

class CommandRunner:
    def __init__(self, governance: GovernanceEngine, level: int = 1, model_name: str = "gpt-oss:20b-cloud", history_mgr=None):
        self.gov = governance
        self.level = level
        self.model_name = model_name
        self.history_mgr = history_mgr
        self.console = Console()

    def run_command(self, cmd: str, capture_pwd: bool = False) -> tuple[int, str]:
        """Executes a command and returns exit code and combined output."""
        is_windows = platform.system() == "Windows"
        try:
            full_cmd = cmd
            if capture_pwd:
                if is_windows:
                    # Windows CMD syntax for capturing PWD
                    full_cmd = f'("{cmd}") & echo. & echo HEY_CWD_HANDOFF:%CD%'
                else:
                    # Unix shell syntax
                    full_cmd = f'{{ {cmd} ; }} ; printf "\\nHEY_CWD_HANDOFF:%s\\n" "$(pwd)"'
            
            result = subprocess.run(
                full_cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True
            )
            
            out = result.stdout
            if capture_pwd and "HEY_CWD_HANDOFF:" in out:
                match = re.search(r"HEY_CWD_HANDOFF:(.*)", out)
                if match:
                    cwd = match.group(1).strip()
                    # Clean up output to hide the marker and the extra newline
                    out = re.sub(r"\n?HEY_CWD_HANDOFF:.*", "", out, flags=re.DOTALL).strip()
                    
                    # Normalize paths for comparison (especially on Windows)
                    norm_cwd = os.path.normpath(cwd).lower() if is_windows else os.path.normpath(cwd)
                    norm_actual = os.path.normpath(os.getcwd()).lower() if is_windows else os.path.normpath(os.getcwd())
                    
                    if norm_cwd != norm_actual:
                        with open(os.path.expanduser("~/.hey_cwd_handoff"), "w") as f:
                            f.write(cwd)
            
            return result.returncode, out
        except Exception as e:
            return -1, str(e)

    def _prompt_user(self, prompt: str) -> bool:
        try:
            sys.stdout.write(f"{prompt} ")
            sys.stdout.flush()
            ans = sys.stdin.readline().strip().lower()
            return ans in ('y', 'yes')
        except KeyboardInterrupt:
            print("\nAborted.")
            return False

    def _prompt_exact(self, prompt: str, expected_match: str) -> bool:
        try:
            sys.stdout.write(f"\033[93m{prompt}\033[0m ")
            sys.stdout.flush()
            ans = sys.stdin.readline().strip()
            return ans == expected_match
        except KeyboardInterrupt:
            print("\nAborted.")
            return False

    def _check_governance(self, cmd: str) -> bool:
        """Run command through governance and output proper CLI prompts."""
        action, reason = self.gov.evaluate(cmd)
        
        if action == Action.BLOCKED:
            self.console.print(f"[bold red]● [BLOCKED][/bold red] {reason}")
            return False
            
        elif action == Action.EXPLICIT_CONFIRM:
            self.console.print(f"[bold yellow]● [WARNING] High risk command detected![/bold yellow]")
            if not self._prompt_exact(f"Type '{reason}' to confirm execution:", reason):
                self.console.print("[dim]Confirmation failed. Aborted.[/dim]")
                return False
            return True
            
        elif action == Action.YN_CONFIRM:
            if self.level >= 2:
                if self.level == 2:
                    self.console.print(f"[dim]● Auto-approving (Level {self.level}): {reason}[/dim]")
                return True
            if not self._prompt_user("Execute this command? [y/N]:"):
                 self.console.print("[dim]Aborted.[/dim]")
                 return False
            return True
            
        elif action == Action.PROCEED:
            # Completely silent for PROCEED
            return True
            
        return False

    def execute_flow(self, initial_response: CommandResponse, original_objective: str):
        current_response = initial_response
        current_context = ""
        
        # Micro-Agent Context Gathering Loop (Active for Level 1, 2)
        if self.level in (1, 2):
            iteration = 0
            executed_commands = set()
            while current_response.needs_context and iteration < 5:
                cmd_stripped = current_response.command.strip()
                if cmd_stripped in executed_commands:
                    self.console.print(f"[bold red]●[/bold red] Loop detected on: [bold]{cmd_stripped}[/bold]. Forcing final answer.")
                    current_context += f"\n\n[System]: You already ran '{cmd_stripped}'. Stop gathering context and provide the final answer with needs_context=false."
                    current_response = generate_command(original_objective, context=current_context, model_name=self.model_name)
                    iteration += 1
                    continue
                    
                executed_commands.add(cmd_stripped)
                self.console.print(f"[bold cyan]●[/bold cyan] [bold]{current_response.command}[/bold]")
                if not self._check_governance(current_response.command):
                    self.console.print(f"[bold red]●[/bold red] Context gathering blocked by governance. Reverting to manual answer.")
                    break
                    
                code, out = self.run_command(current_response.command)
                clean_out = out.strip()
                if len(clean_out) > 5000:
                    clean_out = clean_out[:5000] + "\n...[Output Truncated]"
                    
                current_context += f"\n\n[Output of {current_response.command}]:\n{clean_out}"
                
                self.console.print("[bold dim]● Analyzing output...[/bold dim]")
                current_response = generate_command(original_objective, context=current_context, model_name=self.model_name)
                iteration += 1

        cmd = current_response.command.strip() if current_response.command else ""
        
        # Save final outcome to history
        if self.history_mgr:
            if not cmd or cmd.startswith("echo ") or cmd.startswith("printf "):
                self.history_mgr.append("assistant", current_response.explanation)
            else:
                self.history_mgr.append("assistant", json.dumps(dataclasses.asdict(current_response)))

        # Level 0 = Dry Run
        if self.level == 0:
            self.console.print("[dim]● Dry run (Level 0). Exiting without execution.[/dim]")
            return

        if not cmd:
            self.console.print("\n[bold green]● TASK RESULT:[/bold green]")
            self.console.print(Markdown(current_response.explanation))
            return

        # Action mode (command generated)
        if self.level != 3:
            if current_response.explanation:
                self.console.print("\n[bold green]● TASK RESULT:[/bold green]")
                self.console.print(Markdown(current_response.explanation))
            self.console.print(f"Command: [bold yellow]{cmd}[/bold yellow]\n")

        # Levels 1 and 2
        if self.level in (1, 2):
            if self._check_governance(cmd):
                self.console.print(f"[bold green]● Running:[/bold green] {cmd}")
                code, out = self.run_command(cmd, capture_pwd=True)
                if out.strip():
                    print(out.strip())
                sys.exit(code)
            else:
                sys.exit(1)

        # Level 3 = Iterative Troubleshooter
        if self.level == 3:
            history = []
            current_cmd = cmd
            
            print("\033[96m[hey]\033[0m Iterative Troubleshooter Started:")
            
            tr = None
            for iteration in range(1, 6): # Max 5 iterations
                if not self._check_governance(current_cmd):
                    print("  \033[91m-> Blocked by governance.\033[0m")
                    break
                    
                print(f"  \033[93mStep {iteration}\033[0m: \033[1m{current_cmd}\033[0m", end=" ")
                code, out = self.run_command(current_cmd)
                
                clean_out = out.strip()
                if clean_out:
                    print(f"\n  \033[90m> {clean_out[:200]}{'...' if len(clean_out) > 200 else ''}\033[0m")
                else:
                    print(f" \033[92m(done)\033[0m")
                
                history.append({
                    "cmd": current_cmd,
                    "exit_code": code,
                    "output": clean_out
                })
                
                tr = generate_troubleshoot_step(original_objective, history, model_name=self.model_name)
                if tr.is_resolved:
                    print(f"\n\033[92m[hey] {tr.explanation}\033[0m")
                    sys.exit(0)
                    
                current_cmd = tr.command
                if not current_cmd:
                    print(f"\n\033[92m[hey] {tr.explanation}\033[0m")
                    sys.exit(0)

            if tr:
                print(f"\n\033[93m[hey] Pausing after 5 steps. Final assessment:\033[0m")
                print(f"\033[92m{tr.explanation}\033[0m")
            sys.exit(0)
