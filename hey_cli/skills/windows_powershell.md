# Windows (PowerShell) Skills
# PowerShell cmdlets, completely different syntax from Unix

- Directory listing: `Get-ChildItem` (alias `dir`, `ls`).
- Change directory: `Set-Location` (alias `cd`).
- Copy: `Copy-Item`. Move: `Move-Item`. Remove: `Remove-Item`.
- Create directory: `New-Item -ItemType Directory -Name <name>`.
- Create file: `New-Item -ItemType File -Name <name>`.
- Search text: `Select-String -Path <file> -Pattern '<regex>'`, not `grep`.
- IP address: `ipconfig`. Detailed: `Get-NetIPAddress`.
- DNS flush: `ipconfig /flushdns`.
- Process list: `Get-Process`. Kill: `Stop-Process -Id <pid>` or `Stop-Process -Name <name>`.
- Process on port: `Get-NetTCPConnection -LocalPort <port>`.
- Service management: `Get-Service`, `Start-Service`, `Stop-Service`, `Restart-Service`.
- Package manager: `winget install <pkg>` or `choco install <pkg>` or `scoop install <pkg>`.
- Download file: `Invoke-WebRequest -Uri <url> -OutFile <file>`.
- Extract archive: `Expand-Archive -Path <file> -DestinationPath <dir>`.
- Compress: `Compress-Archive -Path <source> -DestinationPath <dest>.zip`.
- Open file/URL: `Start-Process <path_or_url>`.
- Clipboard: `Set-Clipboard`, `Get-Clipboard`.
- Environment variables: `$env:VARIABLE_NAME`. Set: `$env:VAR = "value"`.
- Paths use backslash `\`, not forward slash `/`.
- Piping works differently: PowerShell pipes objects, not text streams.
- Use `Where-Object`, `ForEach-Object`, `Sort-Object` for filtering/processing.
