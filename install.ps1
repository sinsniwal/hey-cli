<#
.SYNOPSIS
Installs hey-cli natively across Windows architectures.
.DESCRIPTION
This script verifies Python is installed, forces a user-level pipx installation,
validates Ollama runtime logic, downloads the default specified model, and natively builds hey.
#>

$ErrorActionPreference = "Stop"
$ModelName = "gpt-oss:20b-cloud"

Write-Host "Welcome to the hey-cli Windows installer!" -ForegroundColor Cyan
Write-Host "This script will setup Python dependencies, verify Ollama, and explicitly build hey-cli locally.`n"

# 1. Check Python
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✔️  $pythonVersion found." -ForegroundColor Green
} catch {
    Write-Host "Error: python is not installed or not in PATH. Please install Python 3.9+ from python.org or the Microsoft Store first." -ForegroundColor Red
    Exit 1
}

# 2. Setup pipx
try {
    $pipxCheck = & pipx --version 2>&1
    Write-Host "✔️  pipx found." -ForegroundColor Green
} catch {
    Write-Host "pipx not found. Installing via python..." -ForegroundColor Cyan
    & python -m pip install --user pipx
    & python -m pipx ensurepath
    Write-Host "pipx installed successfully. Note: You may need to restart your terminal for pipx path to register." -ForegroundColor Yellow
}

# 3. Setup Ollama
try {
    $ollamaCheck = & ollama --version 2>&1
    Write-Host "✔️  Ollama found." -ForegroundColor Green
} catch {
    Write-Host "`nOllama is not installed. Automatic headless install on Windows is unsupported natively." -ForegroundColor Red
    Write-Host "Please download and run the Ollama Windows installer here: https://ollama.com/download/windows" -ForegroundColor Yellow
    Write-Host "Once installed, run this script again!"
    Exit 1
}

# 4. Pull Default Model
Write-Host "`nPulling default language model ($ModelName)..." -ForegroundColor Cyan
Write-Host "This may take several minutes depending on your network..." -ForegroundColor Gray
try {
    & ollama pull $ModelName
} catch {
    Write-Host "Warning: Could not pull $ModelName. Please ensure the Ollama application is running in your system tray." -ForegroundColor Red
}

# 5. Install hey-cli
Write-Host "`nInstalling hey-cli-python..." -ForegroundColor Cyan
& pipx install hey-cli-python --force

Write-Host "`n============ SUCCESS =============" -ForegroundColor Green
Write-Host "hey-cli is successfully installed!"
Write-Host "You may need to restart your PowerShell window for the 'hey' alias to be recognized."
Write-Host "Test it out by typing: " -NoNewline
Write-Host "hey is docker running" -ForegroundColor Cyan
