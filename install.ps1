<#
.SYNOPSIS
Installs hey-cli natively across Windows architectures.
.DESCRIPTION
This script verifies Python is installed, forces a user-level pipx installation,
validates Ollama runtime logic, downloads the default specified model, and natively builds hey.

Alternative install methods (no Python required):
  Scoop:  scoop install https://raw.githubusercontent.com/sinsniwal/hey-cli/main/scoop/hey-cli.json
  Winget: winget install hey-cli
#>

$ErrorActionPreference = "Stop"
$ModelName = "gpt-oss:20b-cloud"

Write-Host "Welcome to the hey-cli Windows installer!" -ForegroundColor Cyan
Write-Host "This script will setup Python dependencies, verify Ollama, and build hey-cli locally."
Write-Host ""

# 1. Check Python
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[OK] $pythonVersion found." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://python.org or the Microsoft Store." -ForegroundColor Yellow
    Exit 1
}

# 2. Setup pipx
try {
    $pipxCheck = & pipx --version 2>&1
    Write-Host "[OK] pipx found." -ForegroundColor Green
} catch {
    Write-Host "pipx not found. Installing via python..." -ForegroundColor Cyan
    & python -m pip install --user pipx
    & python -m pipx ensurepath
    Write-Host "pipx installed. You may need to restart your terminal for the pipx path to register." -ForegroundColor Yellow
}

# 3. Setup Ollama
try {
    $ollamaCheck = & ollama --version 2>&1
    Write-Host "[OK] Ollama found." -ForegroundColor Green
} catch {
    Write-Host "" 
    Write-Host "[ERROR] Ollama is not installed." -ForegroundColor Red
    Write-Host "Please download the Ollama Windows installer: https://ollama.com/download/windows" -ForegroundColor Yellow
    Write-Host "Once installed, run this script again."
    Exit 1
}

# 4. Authenticate with Ollama
Write-Host ""
Write-Host "Authenticating with Ollama..." -ForegroundColor Cyan
Write-Host "If prompted, sign in with your Ollama account."
try {
    & ollama login
    Write-Host "[OK] Authentication complete." -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Authentication skipped. You may see 401 errors if your Ollama instance requires auth." -ForegroundColor Yellow
}

# 5. Pull Default Model
Write-Host ""
Write-Host "Pulling default language model ($ModelName)..." -ForegroundColor Cyan
Write-Host "This may take several minutes depending on your network..." -ForegroundColor Gray
try {
    & ollama pull $ModelName
} catch {
    Write-Host "[WARNING] Could not pull $ModelName. Ensure Ollama is running in your system tray." -ForegroundColor Red
}

# 6. Install hey-cli
Write-Host ""
Write-Host "Installing hey-cli-python..." -ForegroundColor Cyan
& pipx install hey-cli-python --force

Write-Host ""
Write-Host "============ SUCCESS =============" -ForegroundColor Green
Write-Host "hey-cli is successfully installed!"
Write-Host "You may need to restart your PowerShell window for the 'hey' command to be recognized."
Write-Host "Test it out by typing: " -NoNewline
Write-Host "hey is docker running" -ForegroundColor Cyan
