---
name: New OS Skill Template 🧠
about: Submit heuristics to drastically improve hey-cli on a specific OS
title: "[SKILL] Add heuristics for <OS Name>"
labels: enhancement, skill-engine
assignees: ''

---

## 🧠 Skill Request Overview
What OS or distribution are you adding heuristics for? (e.g., NixOS, FreeBSD, ChromeOS, Alpine).

**Target OS:** [Insert OS here]
**Default Shell:** [e.g., ash, bash, zsh]
**Package Manager:** [e.g., nix-env, apk, pkg]

## 🛠 Command Quirks & Divergences
List the specific terminal commands that fail natively, and what `hey-cli` SHOULD do instead. 

- **Sed in-place:** [e.g., `sed -i ''` or `sed -i`?]
- **Grep regex:** [Is `grep -P` supported?]
- **Clipboard tools:** [Does it use xclip, pbcopy, wayland?]
- **Any other quirks:** [What makes this OS unique?]

## 📄 Proposed Markdown Addition
Please paste your proposed Markdown ruleset below. This will be integrated directly into `hey_cli/skills/<os_name>.md`.

```markdown
# [OS Name] Skills

- For in-place sed replacement, use...
- Never use xargs without...
- Package manager is...
```

## 🧪 Verification
- [ ] I am actively running this OS right now.
- [ ] I have verified these shell constraints manually.
