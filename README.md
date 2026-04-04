<div align="center">
  <h1>hey-cli</h1>
  <p><strong>Your terminal buddy that turns plain English into shell scripts — and runs them for you.</strong></p>

  <a href="https://pypi.org/project/hey-cli-python/"><img src="https://img.shields.io/pypi/v/hey-cli-python?label=PyPI&color=blue" alt="PyPI" /></a>
  <img src="https://img.shields.io/pypi/pyversions/hey-cli-python?color=blue" alt="Python" />
  <a href="https://github.com/sinsniwal/hey-cli/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" /></a>
  <a href="https://github.com/sinsniwal/hey-cli/releases/latest"><img src="https://img.shields.io/github/v/release/sinsniwal/hey-cli?label=Release&color=orange" alt="Release" /></a>
</div>

<br>

`hey` is a terminal-native AI assistant that translates plain English into executable shell commands using a locally-hosted LLM via [Ollama](https://ollama.com). Your data never leaves your machine.

```
$ hey find all python files modified in the last 24 hours
● Thinking...

▶ find . -name "*.py" -mtime -1 -type f

Run this command? [Y/n]:
```

---

## Features

- **100% Local & Private** — All reasoning happens on your machine via Ollama. No API keys, no cloud, no telemetry.
- **Cross-Platform Intelligence** — Detects your OS (macOS/Linux/Windows) and generates the correct flags. Won't suggest `xargs -d` on BSD or `apt` on Arch.
- **Agentic Context Gathering** — Ask "is Docker running?" and `hey` silently runs diagnostics, reads the output, and answers in plain English.
- **Security Governance** — Dangerous commands (`rm -rf`, `mkfs`, `DROP TABLE`) are intercepted and require explicit confirmation before execution.
- **Pipe-Friendly** — Pipe error logs directly: `npm run build 2>&1 | hey what is causing this error?`
- **Conversational Memory** — Remembers your recent interactions for follow-up questions.

---

## Installation

`hey` requires [Ollama](https://ollama.com) running locally. Install it first, then choose your platform:

### macOS (Homebrew)

```bash
brew tap sinsniwal/hey-cli
brew install hey-cli
```

> [!TIP]
> **Apple Silicon (M1/M2/M3) Note:** If you see an error about `Rosetta 2` while installing via Homebrew, ensure your terminal is running natively (not under Rosetta emulation). You can force a native installation by running:
> `arch -arm64 brew install hey-cli`

### macOS & Linux (curl)

```bash
curl -sL https://raw.githubusercontent.com/sinsniwal/hey-cli/main/install.sh | bash
```

### Windows (Scoop)

```powershell
scoop install https://raw.githubusercontent.com/sinsniwal/hey-cli/main/scoop/hey-cli.json
```

### Windows (PowerShell Installer)

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/sinsniwal/hey-cli/main/install.ps1" -OutFile "$env:TEMP\hey_install.ps1"; & "$env:TEMP\hey_install.ps1"
```

### Windows (Standalone Binary)

Download `hey.exe` from the [latest release](https://github.com/sinsniwal/hey-cli/releases/latest). No Python required.

### pip / pipx

```bash
pipx install hey-cli-python
```

> **Note:** After installation, pull the default model: `ollama pull gpt-oss:20b-cloud`

---

## Usage

```bash
hey <your objective in plain English>
```

### Examples

| Command | What happens |
|---------|-------------|
| `hey list all running docker containers` | Generates and runs `docker ps` |
| `hey is port 8080 in use?` | Silently runs `lsof -i :8080`, reads output, answers in English |
| `hey forcefully delete all .pyc files` | Generates `find . -name "*.pyc" -delete`, pauses for confirmation |
| `hey compress this folder into a tar.gz` | Generates the correct `tar` command for your OS |
| `npm run build 2>&1 \| hey what broke?` | Reads piped stderr and explains the error |
| `hey --clear` | Wipes conversational memory |

### Execution Levels

| Level | Flag | Behavior |
|-------|------|----------|
| 0 | `--level 0` | Dry-run — shows the command but never executes |
| 1 | *(default)* | Supervised — safe commands auto-run, risky ones ask for confirmation |
| 2 | `--level 2` | Unrestricted — executes everything without confirmation |
| 3 | `--level 3` | Troubleshooter — iteratively debugs until the objective is resolved |

---


---

## Authentication & Custom Endpoints

`hey` works locally by default, but it also supports authenticated Ollama instances and custom hosts:

- **Standard Login:** Most users should run `ollama login` once to authenticate their terminal with the local or cloud instance.
- **Auth Key:** If you are in a CI/CD or server environment, you can set the `OLLAMA_API_KEY` environment variable.
- **Custom Host:** If Ollama is running on a different port or machine, set `OLLAMA_HOST` (e.g., `export OLLAMA_HOST="http://192.168.1.10:11434"`).
- **Custom Model:** You can provide a custom model via `--model`:
  ```bash
  hey "summarize this file" --model llama3
  ```

---

## Security

Safety is enforced at runtime via a local governance engine (`~/.hey-rules.json`):

- **Blocked** — `rm -rf /`, `mkfs`, `:(){ :|:& };:` are permanently rejected.
- **Explicit Confirm** — High-risk operations (`rm`, `truncate`, `DROP`) require typing a keyword to authorize.
- **Y/N Confirm** — Moderate-risk operations require a quick `y`.
- **Auto-Run** — Safe diagnostics (`ls`, `cat`, `grep`, `git status`) execute immediately.

Initialize or customize your rules:

```bash
hey --init
```

---

## OS Skills

`hey` ships with built-in knowledge for macOS, Ubuntu/Debian, Arch Linux, Fedora/RHEL, Windows PowerShell, FreeBSD, and ChromeOS.

**Want to improve it for your OS?** Add a Markdown file to `hey_cli/skills/` with plain-English rules (e.g., "On Alpine, use `apk add` instead of `apt install`"). The engine loads them dynamically at runtime.

Pull requests for new OS skills are welcome!

---

## Architecture

```
hey "your question"
    │
    ▼
┌──────────────┐     ┌──────────────────┐
│  CLI Parser  │────▶│ Governance Check │
└──────────────┘     └────────┬─────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Ollama (local LLM)│
                    │  localhost:11434   │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Command Runner    │
                    │  (execute / confirm)│
                    └────────────────────┘
```

- **Zero external API calls** — communicates with Ollama via `localhost:11434` using Python's built-in `urllib`.
- **Zero compiled dependencies** — the only runtime dependency is `rich` (for terminal formatting).
- **Pure Python 3.9–3.14** — no C extensions, no Rust, no build tools required.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

See [RELEASING.md](RELEASING.md) for maintainer release instructions.

---

## License

[MIT](LICENSE) — Mohit Singh Sinsniwal
