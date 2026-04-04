# hey-cli Release Runbook

Everything is automated via GitHub Actions. Publishing a release triggers **all three channels** in parallel.

---

## One-Time Setup: GitHub Secrets

Go to **GitHub → Settings → Secrets and variables → Actions** and add:

| Secret Name           | Value                                      |
|-----------------------|--------------------------------------------|
| `PYPI_API_TOKEN`      | Your PyPI API token (starts with `pypi-`)  |
| `HOMEBREW_TAP_TOKEN`  | A GitHub PAT with `repo` scope (to push to `sinsniwal/homebrew-hey-cli`) |

---

## How to Release a New Version

### 1. Bump the version in `pyproject.toml`

```toml
version = "X.Y.Z"
```

### 2. Commit and push

```bash
git add .
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

### 3. Create a GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - <short description>" \
  --notes "<changelog notes>"
```

### 4. Done! 🎉

The `release.yml` workflow automatically:

| Step | What it does | Channel |
|------|-------------|---------|
| **Job 1** | Builds `.tar.gz` + `.whl`, uploads to PyPI | `pip install hey-cli-python` |
| **Job 2** | Waits for PyPI, regenerates `hey-cli.rb`, pushes to homebrew tap | `brew install hey-cli` |
| **Job 3** | Compiles `hey.exe` via PyInstaller, attaches to the GitHub Release | Scoop / Winget / direct download |

---

## Updating Scoop Manifest

After a release, bump the version in `scoop/hey-cli.json`:

```json
"version": "X.Y.Z"
```

Commit and push — Scoop's `autoupdate` block handles the rest.

---

## Manual Fallback

If CI fails for any reason, you can still release manually:

```bash
# PyPI
rm -rf dist/ build/ && python -m build && python -m twine upload dist/*

# Homebrew
python scripts/generate_brew.py
cd ~/github/homebrew-hey-cli && git add . && git commit -m "Update" && git push

# Windows (trigger workflow manually)
gh workflow run release.yml
```
