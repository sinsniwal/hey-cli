<#
.SYNOPSIS
Installs hey-cli natively across Windows architectures.
.DESCRIPTION
This script verifies Python is installed, forces a user-level uv installation,
validates Ollama runtime logic, downloads the default specified model, and natively builds hey.

Alternative install methods (no Python required):
  Scoop:  scoop install https://raw.githubusercontent.com/sinsniwal/hey-cli/main/scoop/hey-cli.json
  Winget: winget install hey-cli
#>

$ErrorActionPreference = "Stop"
$ModelName = "gpt-oss:20b-cloud"

Write-Host "Welcome to the hey-cli Windows installer!" -ForegroundColor Cyan
Write-Host "This script will setup uv and Python dependencies, verify Ollama, and build hey-cli locally."
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

# 2. Setup uv
try {
    $uvCheck = & uv --version 2>&1
    Write-Host "[OK] uv found." -ForegroundColor Green
} catch {
    Write-Host "uv not found. Installing via official script..." -ForegroundColor Cyan
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    # Update current session path
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
    
    if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] uv installation failed or not in PATH." -ForegroundColor Red
        Write-Host "Please install uv manually: https://github.com/astral-sh/uv" -ForegroundColor Yellow
        Exit 1
    }
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

# Ensure Ollama is running before proceeding
Write-Host ""
Write-Host "Verifying Ollama server status..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
} catch {
    Write-Host "Ollama server is not running. Attempting to start..." -ForegroundColor Yellow
    # Windows: Start Ollama app from common locations
    $ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
    if (Test-Path $ollamaExe) {
        Start-Process $ollamaExe
    } else {
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    }
    
    Write-Host -NoNewline "Waiting for Ollama to boot"
    for ($i=0; $i -lt 15; $i++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
            Write-Host " [OK]" -ForegroundColor Green
            break
        } catch {
            Write-Host -NoNewline "."
            Start-Sleep -Seconds 2
        }
    }
    Write-Host ""
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
} catch {
    Write-Host "[WARNING] Could not connect to Ollama server at localhost:11434." -ForegroundColor Red
    Write-Host "Please ensure Ollama is running and try again." -ForegroundColor Yellow
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
$installTarget = "hey-cli-python"
if (Test-Path "pyproject.toml") {
    $installTarget = "."
    Write-Host "Detected local pyproject.toml. Installing from source..." -ForegroundColor Gray
}

& uv tool install "$installTarget" --force

Write-Host ""
Write-Host "============ SUCCESS =============" -ForegroundColor Green
Write-Host "hey-cli is successfully installed!"
Write-Host "You may need to restart your PowerShell window for the 'hey' command to be recognized."
Write-Host "Test it out by typing: " -NoNewline
Write-Host "hey hi" -ForegroundColor Cyan
Write-Host ""

# 7. Automated Shell Integration
if ($null -ne $PROFILE) {
    Write-Host "Would you like to enable directory persistence (making 'cd' work)? [y/N]" -ForegroundColor Yellow
    $confirm = Read-Host "> "
    if ($confirm -match "^[Yy]$") {
        # Ensure profile directory exists
        $profileDir = Split-Path -Path $PROFILE
        if (!(Test-Path $profileDir)) {
             New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
        }
        # Ensure profile file exists
        if (!(Test-Path $PROFILE)) {
             New-Item -ItemType File -Path $PROFILE -Force | Out-Null
        }
        
        $initLine = "hey --shell-init | Out-String | iex"
        if (!(Select-String -Path $PROFILE -Pattern "hey --shell-init" -Quiet)) {
            Add-Content -Path $PROFILE -Value "`n# hey-cli shell integration`n$initLine"
            Write-Host "[OK] Added shell integration to $PROFILE. Please restart PowerShell." -ForegroundColor Green
        } else {
            Write-Host "[OK] Shell integration already exists in $PROFILE." -ForegroundColor Green
        }
    } else {
        Write-Host "Skipping shell integration. You can always add it later manually." -ForegroundColor Gray
    }
} else {
    Write-Host "Tip: To enable 'cd' persistence, add this to your PowerShell profile:" -ForegroundColor Yellow
    Write-Host "hey --shell-init | Out-String | iex" -ForegroundColor Cyan
}
