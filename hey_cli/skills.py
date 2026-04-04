"""
Modular skills registry for hey-cli.
Dynamically loads OS-specific and universal shell heuristics from markdown files
in the skills/ directory and injects them into the LLM system prompt.

Add new skills by creating/editing .md files in hey_cli/skills/:
  - shell.md        → Universal rules (applied on ALL platforms)
  - darwin.md       → macOS specific
  - ubuntu_debian.md → Ubuntu/Debian specific
  - fedora_rhel.md  → Fedora/RHEL/CentOS specific
  - arch_linux.md   → Arch/Manjaro specific
  - windows_powershell.md → Windows PowerShell
  - windows_wsl.md  → WSL specific
  - alpine.md       → Alpine Linux specific
  - freebsd.md      → FreeBSD specific
  - opensuse.md     → openSUSE/SLES specific
  - chromeos.md     → ChromeOS Crostini specific
"""

import platform
from pathlib import Path

# Map platform.system() output to skill file basenames
OS_SKILL_MAP = {
    "Darwin": ["darwin"],
    "Linux": [],       # Resolved dynamically below based on distro detection
    "Windows": ["windows_powershell"],
    "FreeBSD": ["freebsd"],
}

# Linux distro detection → skill file mapping
LINUX_DISTRO_MAP = {
    "ubuntu": "ubuntu_debian",
    "debian": "ubuntu_debian",
    "pop": "ubuntu_debian",       # Pop!_OS
    "mint": "ubuntu_debian",      # Linux Mint
    "fedora": "fedora_rhel",
    "rhel": "fedora_rhel",
    "centos": "fedora_rhel",
    "rocky": "fedora_rhel",       # Rocky Linux
    "alma": "fedora_rhel",        # AlmaLinux
    "arch": "arch_linux",
    "manjaro": "arch_linux",
    "endeavouros": "arch_linux",
    "alpine": "alpine",
    "opensuse": "opensuse",
    "sles": "opensuse",
    "suse": "opensuse",
    "chromeos": "chromeos",
}

SKILLS_DIR = Path(__file__).parent / "skills"


def _detect_linux_distro() -> str:
    """Detect Linux distribution from /etc/os-release."""
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read().lower()
            for key, skill_file in LINUX_DISTRO_MAP.items():
                if key in content:
                    return skill_file
    except FileNotFoundError:
        pass
    
    # Fallback: check for WSL
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return "windows_wsl"
    except FileNotFoundError:
        pass
    
    # Default to ubuntu_debian as most common
    return "ubuntu_debian"


def _load_skill_file(filename: str) -> str:
    """Load a skill markdown file and return its content as plain text."""
    filepath = SKILLS_DIR / f"{filename}.md"
    if filepath.exists():
        return filepath.read_text(encoding="utf-8").strip()
    return ""


def get_compiled_skills() -> str:
    """
    Compiles a formatted string of applicable operational skills
    based on host OS and distro. Always includes shell.md (universal).
    """
    os_name = platform.system()
    
    # Always load universal shell skills
    sections = []
    shell_content = _load_skill_file("shell")
    if shell_content:
        sections.append(shell_content)
    
    # Load OS-specific skills
    os_files = OS_SKILL_MAP.get(os_name, [])
    
    # For Linux, detect the specific distro
    if os_name == "Linux":
        distro_file = _detect_linux_distro()
        os_files = [distro_file]
    
    for skill_file in os_files:
        content = _load_skill_file(skill_file)
        if content:
            sections.append(content)
    
    if not sections:
        return ""
    
    return "### OPERATIONAL SKILLS & HEURISTICS\n\n" + "\n\n---\n\n".join(sections)
