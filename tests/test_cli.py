import pytest
import os
import platform
from hey_cli.llm import generate_command
from hey_cli.governance import GovernanceEngine, Action

def test_governance_engine_safe_command():
    gov = GovernanceEngine()
    # Explicitly test an allowed command
    action, keyword = gov.evaluate("ls -la")
    assert action == Action.PROCEED

def test_governance_engine_unsafe_command():
    gov = GovernanceEngine()
    # Explicitly test a blocked command
    action, keyword = gov.evaluate("rm -rf /")
    assert action == Action.BLOCKED
    
def test_governance_engine_explicit_confirm():
    gov = GovernanceEngine()
    # Explicit test for dangerous keywords
    action, keyword = gov.evaluate("find . -name temp -exec rm -f {} +")
    assert action == Action.EXPLICIT_CONFIRM
    assert keyword in ["-exec", "rm"]

def test_system_prompt_structure():
    from hey_cli.llm import SYSTEM_PROMPT
    assert "CRITICAL PARSING RULE:" in SYSTEM_PROMPT
    assert "needs_context" in SYSTEM_PROMPT

def test_skill_compiler():
    from hey_cli.skills import get_compiled_skills
    skills = get_compiled_skills()
    assert isinstance(skills, str)
    # The universal shell sheet is always loaded
    assert "Universal Shell Skills" in skills
    # The OS-specific sheet should be loaded dynamically
    os_name = platform.system()
    if os_name == "Windows":
        assert "Windows" in skills
    elif os_name == "Darwin":
        assert "macOS" in skills
