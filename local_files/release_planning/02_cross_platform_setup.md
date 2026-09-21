# Cross-Platform Setup & Installation Plan

If we want `hey-cli` to blow up, it must be completely frictionless to install. "Any person using any platform."

## 1. Python Package Index (PyPI)
Publish `hey-cli` to PyPI. 
Users will install it via:
```bash
pipx install hey-cli
```
*Note: We recommend `pipx` over `pip install -g` because Python 3.11+ strictly blocks global pip installs natively (PEP 668).*

## 2. macOS (Homebrew)
Mac developers expect to use `brew`. We should create a Homebrew Tap:
- Auto-compiles the bash wrapper and Python dependencies.
```bash
brew tap sinsniwal/hey-cli
brew install hey-cli
```

## 3. Linux (Apt, AUR, DNF)
- **Arch Users**: Publish a PKGBUILD for the AUR (`yay -S hey-cli`).
- **Debian/Ubuntu**: A generic setup script `curl -sL https://hey-cli.dev/install.sh | bash` that gracefully bridges the python environment.

## 4. Windows (Scoop / Winget)
Windows has the hardest time with Python CLIs.
- Bundle an executable or ensure the `pyproject.toml` `[project.scripts]` entry correctly builds the `hey.exe` wrapper during pip installation.
- Recommended installation path: `winget install hey-cli`.

## 5. Dependency Handing (Ollama)
`hey-cli` depends on a local language model. 
- The installation script **must** check if `ollama` is installed and running on the system (`localhost:11434`). 
- If not found, print a bold `rich` ASCII prompt instructing them to run `curl -fsSL https://ollama.com/install.sh | sh` before running `hey`.
