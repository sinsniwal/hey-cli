import json
import os
from pathlib import Path

class HistoryManager:
    def __init__(self, path: str = "~/.hey-history.json", max_messages: int = 15):
        self.path = Path(os.path.expanduser(path))
        self.max_messages = max_messages

    def load(self) -> list:
        if not self.path.exists():
            return []
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def append(self, role: str, content: str):
        history = self.load()
        history.append({"role": role, "content": content})
        
        # Enforce rolling window
        if len(history) > self.max_messages:
            history = history[-self.max_messages:]
            
        with open(self.path, "w") as f:
            json.dump(history, f, indent=2)

    def clear(self):
        if self.path.exists():
            self.path.unlink()
