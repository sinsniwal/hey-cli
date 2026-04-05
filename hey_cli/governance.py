import json
import os
from pathlib import Path

DEFAULT_RULES = {
    "config": {
        "default_level": 1,
        "model": "gpt-oss:20b-cloud"
    },
    "never": [
        "rm -rf /", 
        "mkfs", 
        "dropdb",
        "chmod -R 777"
    ],
    "require_confirmation": [
        "docker run", 
        "docker build", 
        "npm publish", 
        "git push",
        "kubectl delete"
    ],
    "allowed": [
        "ls", "cat", "pwd", "grep", "find", "echo", "tail", "cd"
    ],
    "high_risk_keywords": [
        "reset", "delete", "drop", "truncate", "prune", "rm", "-exec", ">"
    ]
}

class Action(str):
    BLOCKED = "blocked"
    EXPLICIT_CONFIRM = "explicit_confirm"
    YN_CONFIRM = "yn_confirm"
    PROCEED = "proceed"

class GovernanceEngine:
    def __init__(self, rules_path: str = "~/.hey-rules.json"):
        self.rules_path = Path(os.path.expanduser(rules_path))
        self.rules = self._load()

    def _load(self):
        if not self.rules_path.exists():
            return DEFAULT_RULES
        with open(self.rules_path, "r") as f:
            return json.load(f)

    def init_rules(self):
        if not self.rules_path.exists():
            with open(self.rules_path, "w") as f:
                json.dump(DEFAULT_RULES, f, indent=2)
            return True
        return False

    def evaluate(self, command: str) -> tuple[str, str]:
        """
        Evaluate a command against the security matrix.
        Returns a tuple: (Action, Reason/Keyword)
        """
        if not command:
             return Action.BLOCKED, "Empty command"
             
        # 1. Never List
        for never_cmd in self.rules.get("never", []):
            if never_cmd in command:
                 return Action.BLOCKED, f"Matches never list: {never_cmd}"
                 
        # 2. High Risk
        for hr_kw in self.rules.get("high_risk_keywords", []):
            if hr_kw in command:
                 return Action.EXPLICIT_CONFIRM, hr_kw
                 
        # 3. Require Confirmation
        for req_cmd in self.rules.get("require_confirmation", []):
            if req_cmd in command:
                 return Action.YN_CONFIRM, req_cmd
                 
        # 4. Allowed List
        for allow_cmd in self.rules.get("allowed", []):
            # Check if it's the start of the command (e.g. 'ls -la')
            if command.strip().startswith(allow_cmd):
                 return Action.PROCEED, "Allowed command"
        
        # Default behavior: if not explicitly allowed, still require y/N confirm for safety
        return Action.YN_CONFIRM, "Command not explicitly in allowed list"
