# Launch & Marketing Checklist

## Pre-Flight Checks
- [ ] Are all `.pyc` and local debug files deleted from the tree?
- [ ] Does `hey --clear` flawlessly delete local history without crashing if the file is absent?
- [ ] Does the `skills.py` engine correctly load `darwin.md`, `ubuntu_debian.md`, etc., without throwing file-not-found exceptions on fresh installs?
- [ ] Is `rich` properly pinned in `pyproject.toml`?

## Documentation (The README)
The `README.md` is the most important file in the repository.
- [ ] **The "Wow" Header**: An animated `<img src="demo.gif">` showing `hey-cli` dynamically pulling context, executing a safe bash command, and formatting the output natively.
- [ ] **The Elevator Pitch**: "A zero-bloat, privacy-first, locally-hosted CLI agent."
- [ ] **Installation Grid**: Easy one-line copy-paste commands for Mac, Linux, and Windows.
- [ ] **Governance Section**: Explicitly highlight the `~/.hey-rules.json` execution matrix so developers trust the security model (this is a massive selling point!).

## Open-Source Go-To-Market
- [ ] **Product Hunt / Hacker News**: Launch a "Show HN: hey-cli". Developers love locally-hosted (Ollama) privacy tools that don't pipe their terminal data to the cloud.
- [ ] **Reddit**: Post in `r/commandline`, `r/linux`, and `r/LocalLLaMA` emphasizing the custom localized `skills.py` module.
- [ ] **Discord/Community**: Create a channel where users can submit `.md` heuristic rules for edge-case operating systems to be merged into the core OS engine.
