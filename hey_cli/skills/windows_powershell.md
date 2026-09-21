# Windows (PowerShell) Skills
# PowerShell cmdlets, completely different syntax from Unix

## Operational Heuristics
- **Path Separation**: ALWAYS use backslashes `\` for paths. Do NOT use forward slashes.
- **Docker Check**: `docker info > $null 2>&1; if ($?) { echo 'running' } else { echo 'not running' }` (Check if Docker is running via exit code).
- **Process on Port**: `Get-NetTCPConnection -LocalPort <port>` (Equivalent to `lsof -i`).
- **File Search (Content)**: `Select-String -Path .\*.txt -Pattern 'search_term' -Recursive` (Equivalent to `grep -r`).
- **File Search (Filename)**: `Get-ChildItem -Path . -Filter *.log -Recurse` (Equivalent to `find . -name "*.log"`).
- **IP Address**: `(Get-NetIPAddress -AddressFamily IPv4).IPAddress` (Clean IPv4 listing).
- **Environment Variables**: Use `$env:VAR_NAME` to access and `$env:VAR_NAME = "value"` to set for session.
- **Piping**: Remember that PowerShell pipes **objects**, not text. Use `Select-Object`, `Where-Object`, and `ForEach-Object` for filtering.
- **Boolean Logic**: Use `-and`, `-or`, `-not`, `-eq`, `-ne`, `-lt`, `-gt` for comparisons.

## Common Cmdlets
- Directory listing: `Get-ChildItem` (alias `ls`, `dir`).
- Change directory: `Set-Location` (alias `cd`).
- Create directory: `New-Item -ItemType Directory -Name <name>`.
- Create file: `New-Item -ItemType File -Name <name>`.
- Remove: `Remove-Item -Force -Recurse <path>`.
- Download: `Invoke-WebRequest -Uri <url> -OutFile <file>`.
- Extract: `Expand-Archive -Path <file> -DestinationPath <dir>`.
- Process list: `Get-Process`. Kill: `Stop-Process -Id <pid>`.

## Safety
- Execution Policy: If a script fails to run, it may be blocked by `ExecutionPolicy`. Suggest `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the session.
- Avoid `rm -rf` equivalents on system roots.
