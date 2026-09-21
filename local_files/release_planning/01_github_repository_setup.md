# GitHub Repository Structure & CI/CD Plan

## 1. Core Repository Structure
Before pushing to GitHub, ensure the repo is completely clean and standardized:
- `.gitignore`: Exclude `.venv/`, `__pycache__/`, `.env`, and local dotconfig.
- `LICENSE`: Open-source license (MIT highly recommended for CLI utilities).
- `README.md`: The face of the project (needs GIFs, installation matrix).
- `CONTRIBUTING.md`: How community members can add new OS skills to `hey_cli/skills/`.

## 2. GitHub Actions (CI)
We need automated testing to prevent regressions. Since we have OS-specific logic, we must use matrix builds:
- **Matrix OS testing**: Run across `ubuntu-latest`, `macos-latest`, and `windows-latest`.
- **Test Suite**: Run `pytest` against the 100 most used commands logic.
- **Linting**: Enforce `flake8` or `black` formatting to keep contributions clean.

## 3. GitHub Issue Templates
We need standardized issue reporting because CLI errors vary heavily by OS:
- **Bug Report Template**: Must prompt the user for their OS (`platform.system()`), Shell (`bash/zsh/fish`), and the exact command that failed.
- **New Skill Request Template**: To crowdsource heuristic rules for edge-case OSs (like NixOS or ChromeOS).

## 4. Security Scanning
- Enable Dependabot to scan `pyproject.toml` dependencies (`rich`, `ollama`, `pydantic`).
- Ensure no API keys or local `.hey-history.json` payloads are accidentally committed.
