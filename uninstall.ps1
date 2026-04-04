<#
.SYNOPSIS
Uninstalls hey-cli from Windows.
.DESCRIPTION
Removes hey-cli installed via uv, pipx, pip, Scoop, or standalone binary.
Optionally removes configuration files.
#>

$ErrorActionPreference = "Stop"

Write-Host "hey-cli Uninstaller" -ForegroundColor Cyan
Write-Host "This will remove hey-cli and its configuration files."
Write-Host ""

$Removed = $false

# 1. Scoop
try {
    $scoopCheck = & scoop list 2>&1 | Select-String "hey-cli"
    if ($scoopCheck) {
        Write-Host "Removing hey-cli via Scoop..." -ForegroundColor Cyan
        & scoop uninstall hey-cli
        Write-Host "[OK] Scoop package removed." -ForegroundColor Green
        $Removed = $true
    }
} catch {}

# 2. uv
try {
    $uvCheck = & uv tool list 2>&1 | Select-String "hey-cli-python"
    if ($uvCheck) {
        Write-Host "Removing hey-cli via uv..." -ForegroundColor Cyan
        & uv tool uninstall hey-cli-python
        Write-Host "[OK] uv package removed." -ForegroundColor Green
        $Removed = $true
    }
} catch {}

# 3. pipx
try {
    $pipxList = & pipx list 2>&1
    if ($pipxList -match "hey-cli-python") {
        Write-Host "Removing hey-cli via pipx..." -ForegroundColor Cyan
        & pipx uninstall hey-cli-python
        Write-Host "[OK] pipx package removed." -ForegroundColor Green
        $Removed = $true
    }
} catch {}

# 4. pip (fallback)
try {
    $pipShow = & pip show hey-cli-python 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Removing hey-cli via pip..." -ForegroundColor Cyan
        & pip uninstall hey-cli-python -y
        Write-Host "[OK] pip package removed." -ForegroundColor Green
        $Removed = $true
    }
} catch {}

# 5. Standalone binary
$StandalonePath = "$env:LOCALAPPDATA\hey-cli\hey.exe"
if (Test-Path $StandalonePath) {
    Write-Host "Removing standalone binary..." -ForegroundColor Cyan
    Remove-Item $StandalonePath -Force
    Write-Host "[OK] Standalone binary removed." -ForegroundColor Green
    $Removed = $true
}

if (-not $Removed) {
    Write-Host "No hey-cli installation found (checked Scoop, uv, pipx, pip, standalone)." -ForegroundColor Yellow
}

# 5. Config files
Write-Host ""
$ConfigFiles = @(
    "$env:USERPROFILE\.hey-rules.json",
    "$env:USERPROFILE\.hey_history.json"
)

$FoundConfig = $false
foreach ($f in $ConfigFiles) {
    if (Test-Path $f) {
        Write-Host "Found config: $f" -ForegroundColor Yellow
        $FoundConfig = $true
    }
}

if ($FoundConfig) {
    $answer = Read-Host "Remove configuration files? [y/N]"
    if ($answer -eq "y" -or $answer -eq "Y") {
        foreach ($f in $ConfigFiles) {
            if (Test-Path $f) {
                Remove-Item $f -Force
                Write-Host "[OK] Removed $f" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "Keeping configuration files."
    }
}

Write-Host ""
Write-Host "============ DONE =============" -ForegroundColor Green
Write-Host "hey-cli has been uninstalled."
Write-Host "Ollama and your models were NOT removed. To remove Ollama, visit: https://ollama.com"
