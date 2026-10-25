# Поднимает весь локальный стенд в фоне, независимо от окна терминала:
# API (8000), web (5173), туннель localhost.run и бота (через tunnel_supervisor.ps1).
# Остановить всё: scripts\dev_down.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$logs = Join-Path $root ".dev-logs"
New-Item -ItemType Directory -Force $logs | Out-Null

function Test-Port([int]$Port) {
    [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

if (-not (Test-Port 8000)) {
    Start-Process -FilePath (Join-Path $root "apps\api\.venv\Scripts\python.exe") `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" `
        -WorkingDirectory (Join-Path $root "apps\api") -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logs "api.log") -RedirectStandardError (Join-Path $logs "api.err")
}
if (-not (Test-Port 5173)) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev" `
        -WorkingDirectory (Join-Path $root "apps\web") -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logs "web.log") -RedirectStandardError (Join-Path $logs "web.err")
}

$already = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match "powershell" -and $_.CommandLine -match "tunnel_supervisor" }
if (-not $already) {
    Start-Process -FilePath "powershell.exe" -WindowStyle Hidden `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $PSScriptRoot "tunnel_supervisor.ps1")
}
Write-Output "started: api, web, tunnel supervisor (logs: $logs)"
