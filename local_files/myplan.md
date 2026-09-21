# hey-cli: Technical Documentation

**Version:** 1.0.0-draft
**Status:** Active Development
**License:** MIT

## 1. Project Overview

**One-Liner:** `hey` is a secure, zero-bloat CLI companion that turns natural language and error logs into executable commands while you retain absolute control.

**Mission Statement:**
Modern LLM terminal tools are bloated, rely on external API keys, or break the developer's flow state by spawning heavy interactive REPLs. `hey-cli` solves this by providing a single, zero-dependency Python script that bridges your shell directly to a local Ollama instance. It acts as an instant syntax-fixer, a context-aware troubleshooter, and an iterative copilot—all while strictly enforcing your personal security boundaries.

**Core Tenets:**
1. **Flow State Preservation:** Standard I/O only. No new windows, no UI overlays.
2. **Absolute Privacy:** 100% local processing via Ollama. 
3. **Zero Dependencies:** Built entirely on the Python 3 Standard Library.
4. **Strict Governance:** Execution is tightly governed by a local, hard-coded permission matrix.

---

## 2. System Architecture

`hey-cli` operates through four primary subsystems contained within a single executable footprint:

1. **The Context Parser:** Reads standard input (stdin) to capture piped data (e.g., error logs, file contents) and parses CLI arguments to determine your objective.
2. **The LLM Gateway:** Handles asynchronous, dependency-free HTTP communication with your local Ollama REST API (`http://localhost:11434/api/generate`).
3. **The Governance Engine:** Intercepts LLM-generated commands before execution and evaluates them against your `~/.hey-rules.json` security matrix.
4. **The Command Runner:** A state machine that manages execution and handles the iterative troubleshooting loop, always deferring to user permissions.

### Diagram: Execution Flow
```text
[User Input/Stdin] -> Context Parser -> LLM Gateway -> [Ollama]
                                          |
[Terminal/Subprocess] <- Command Runner <- Governance Engine
```

---

## 3. The Governance Engine (Security Model)

To prevent unwanted actions, `hey-cli` enforces a strict permission model via `~/.hey-rules.json`. Every command proposed by the LLM is evaluated against this matrix before it ever reaches your shell.

### Configuration Schema (`~/.hey-rules.json`)
```json
{
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
    "ls", "cat", "pwd", "grep", "find", "echo", "tail"
  ],
  "high_risk_keywords": [
    "reset", "delete", "drop", "truncate", "prune"
  ]
}
```

### Evaluation Logic
1. **Never List:** If the command matches or contains a substring from the `never` list, execution is aggressively aborted.
2. **High-Risk Keywords:** If the command contains a `high_risk_keyword`, the system forces an explicit string-match confirmation (e.g., `Type 'delete' to confirm`).
3. **Require Confirmation:** If matched, the system pauses execution and prompts for a `[y/N]` standard input.
4. **Allowed List:** If matched (and Level 3 is active), the command executes silently.

---

## 4. Execution Levels

`hey` operates across four distinct levels of assistance, defined by the `--level` flag. You dictate how much autonomy the tool has.

### Level 0: Informational (Dry-Run)
* **Behavior:** Acts as a standard query system. It generates the command and prints it to standard output.
* **Use Case:** "How do I do X?"
* **Execution:** None.

### Level 1: Supervised (Default)
* **Behavior:** The standard Copilot mode. Generates the command, presents it to you, and waits for `[y/N]` confirmation before executing.
* **Use Case:** Safe, daily operations and translating natural language to complex bash commands.

### Level 2: Unrestricted (Danger)
* **Behavior:** The "Do It For Me" mode. Bypasses standard `[y/N]` confirmation (though it still respects the `never` list) and auto-executes the generated command.
* **Use Case:** Trusted, isolated environments or highly specific, low-risk requests.

### Level 3: Iterative Troubleshooter
* **Behavior:** Enters an iterative Observation-Action loop. It generates a command, evaluates it against the Governance Engine, runs it, captures `stdout`/`stderr`, and feeds the result back to the LLM to determine the next step to solve your problem.
* **Max Iterations:** Hardcoded limit (default: 5) to prevent infinite loops.
* **Use Case:** Complex, multi-step debugging (e.g., "Find why the build is failing and fix the missing dependencies").

---

## 5. Advanced Integrations

### 5.1 Context Piping
`hey` is designed to ingest standard output from other commands to provide context-aware debugging.

```bash
# Example: Piping a failing test suite directly into the companion
pytest tests/ 2>&1 | hey --level 1 why did this fail and fix it
```

### 5.2 ZSH Auto-Fixer Hook (Instant Cache)
For maximum flow-state retention, `hey-cli` includes an optional ZSH integration that hooks into `command_not_found_handler`. It utilizes a local cache (`~/.hey-cache.json`) to instantly correct muscle-memory typos without invoking the LLM network overhead.

**Implementation (`~/.zshrc`):**
```bash
command_not_found_handler() {
    local cmd=$1
    shift
    local args=("$@")
    
    # Check local cache for O(1) resolution
    local cached_fix=$(hey --check-cache "$cmd")
    
    if [[ -n "$cached_fix" ]]; then
        eval "$cached_fix ${args[@]}"
        return 0
    fi
    
    # Fallback to LLM resolution
    echo -e "\033[93m[hey]\033[0m Command not found. Asking AI..."
    local fix=$(hey --level 1 fix typo "$cmd")
    
    if [[ -n "$fix" ]]; then
        eval "$fix ${args[@]}"
    fi
    return 127
}
```

---

## 6. Installation & Deployment

Because `hey-cli` is a single Python file relying solely on the standard library, deployment is trivial.

### Prerequisites
* Python 3.8+
* [Ollama](https://ollama.com/) running locally.

### Setup
```bash
# 1. Download the executable
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/hey-cli/main/hey.py

# 2. Make it executable
chmod +x hey.py

# 3. Move to your binaries path
sudo mv hey.py /usr/local/bin/hey

# 4. Initialize the Governance Engine (Creates default ~/.hey-rules.json)
hey --init
```