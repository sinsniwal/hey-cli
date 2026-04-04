<div align="center">
  <h1>hey-cli 🤖</h1>
  <p><strong>A zero-bloat, privacy-first, locally-hosted CLI agent powered by Ollama.</strong></p>

  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  <img src="https://img.shields.io/badge/Ollama-Local-orange.svg" alt="Ollama Local" />
</div>

<br>

`hey` isn't just an LLM wrapper. It's a context-aware system agent designed to bridge the gap between human language and POSIX shell utilities natively on your host machine.

> Ask it to parse your error logs, debug Docker, clear DNS caches, or execute complex file maneuvers—all while executing safely behind a dynamic zero-trust governance matrix.

## 🚀 Why `hey-cli` over Copilot/ChatGPT?
1. **Total Privacy**: Your code and system logs never leave your physical CPU. All context gathering and reasoning is done locally via [Ollama](https://ollama.com).
2. **True Cross-Platform Skills**: Under the hood, `hey-cli`'s "Skills Engine" detects if you're on macOS (BSD), Ubuntu (GNU), Windows (PowerShell), or Arch Linux, and actively refuses to generate incompatible flags like `xargs -d` on Mac.
3. **Agentic Execution**: Ask "is docker running?" and `hey` will silently execute `docker info` in the background, read the stdout, analyze it, and return a plain English answer.
4. **Security Governance**: Built-in AST-level parsing. Safe commands (like `git status`) auto-run. Destructive commands (`rm -rf`, `-exec delete`) require explicit typed confirmation.

## 📦 Installation

**Prerequisite:** You must have [Python 3.9+](https://www.python.org/downloads/) installed.

### macOS & Linux
Paste this snippet into your terminal to auto-install `pipx`, `ollama`, pull the required language model, and build `hey-cli` natively.
```bash
curl -sL https://raw.githubusercontent.com/sinsniwal/hey-cli/main/install.sh | bash
```

### Windows (PowerShell)
Paste this into your PowerShell terminal:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/sinsniwal/hey-cli/main/install.ps1" -OutFile "$env:TEMP\hey_install.ps1"; & "$env:TEMP\hey_install.ps1"
```

## 🛠️ Usage

Simply type `hey` followed by your objective.

**Context-Gathering (Zero-Trust)**
```bash
hey is my docker hub running?
```
*`hey` will silently run `systemctl is-active docker` or `docker info`, see that it failed to connect to the socket, and explain the situation.*

**Execution (Governance Protected)**
```bash
hey forcefully delete all .pyc files
```
*`hey` parses the generated `find . -name "*.pyc" -exec rm -f {} +` command, detects `rm` and `-exec` triggers, and pauses execution until you explicitly type `rm` to authorize.*

**Debugging Logs**
```bash
npm run build 2>&1 | hey what is causing this webpack error?
```

## 🛡️ Governance Matrix
Safety is a first-class citizen. `hey-cli` maintains a local governance database (`~/.hey-rules.json`):
- **Never List**: Things like `rm -rf /` and `mkfs` are permanently blocked at the compiler level.
- **Explicit Confirm**: High-risk ops (`truncate`, `drop`, `rm`) require typing exact keyword verification.
- **Y/N Confirm**: Moderate risk ops requiring a quick `y`.
- **Allowed List**: Safe diagnostics like `cat`, `ls`, `grep` auto-run natively.

## 🤝 Adding OS Skills
Is `hey` generating incorrect shell semantics for your niche operating system? 

You can make it permanently smarter without touching code! Simply open `hey_cli/skills/` and create a markdown file for your OS containing explicit English instructions (e.g. "Do not use apt on Alpine, use apk add"). The engine dynamically parses `.md` rulesites at runtime. Pull requests are heavily welcomed!
