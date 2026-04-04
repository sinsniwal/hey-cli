# Winget Publishing Guide

Winget is Microsoft's official Windows Package Manager. Winget officially requires submissions to be PR'd to the `microsoft/winget-pkgs` repository.

Since `hey-cli` now generates a standalone Windows `.exe` using PyInstaller through GitHub Actions, submitting to Winget is incredibly straightforward.

## Prerequisite
You must first draft a GitHub Release (e.g. `v1.0.2`). When you publish the release, our `.github/workflows/windows-release.yml` will automatically build `hey.exe` and attach it to your release assets!

## How to Submit to Winget

1. Open PowerShell on a Windows machine (or use a VM).
2. Install the official Microsoft Winget manifest creation tool:
   ```powershell
   winget install wingetcreate
   ```
3. Run the Winget command to dynamically submit your repository:
   ```powershell
   wingetcreate new https://github.com/sinsniwal/hey-cli/releases/download/v1.0.2/hey.exe
   ```
4. Follow the interactive prompts:
   - **Publisher**: Mohit Singh Sinsniwal
   - **Package**: hey-cli
   - **Version**: 1.0.2
   - **Description**: Zero Bloat AI CLI Context Engine
   - **License**: MIT
   - **Architecture**: X64

5. Once you finish the prompts, `wingetcreate` will automatically fork the `microsoft/winget-pkgs` repo, push your generated YAML manifest cleanly, and instantly open a Pull Request! Once merged by Microsoft (usually in 2-3 days), users worldwide can execute:
   ```powershell
   winget install hey-cli
   ```
