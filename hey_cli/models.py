from pydantic import BaseModel, ConfigDict
from typing import Optional

class CommandResponse(BaseModel):
    command: str
    explanation: str = ""
    needs_context: bool = False

class TroubleshootResponse(BaseModel):
    command: Optional[str] = None
    explanation: str = ""
    is_resolved: bool = False
