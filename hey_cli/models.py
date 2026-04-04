from dataclasses import dataclass
from typing import Optional

@dataclass
class CommandResponse:
    command: str
    explanation: str = ""
    needs_context: bool = False

@dataclass
class TroubleshootResponse:
    command: Optional[str] = None
    explanation: str = ""
    is_resolved: bool = False
