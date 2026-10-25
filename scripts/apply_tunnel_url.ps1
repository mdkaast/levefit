# Привязывает бота к новому публичному адресу туннеля (локальная разработка).
# Использование: powershell -File scripts\apply_tunnel_url.ps1 https://xxxx.lhr.life
# Делает: пишет WEBAPP_URL в apps\api\.env, перезапускает бота, выставляет кнопку меню Mini App.
param([Parameter(Mandatory = $true)][string]$Url)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $root "apps\api\.env"

# 1. WEBAPP_URL в .env
$lines = Get-Content $envFile -Encoding UTF8 | ForEach-Object {
    if ($_ -like "WEBAPP_URL=*") { "WEBAPP_URL=$Url" } else { $_ }
}
Set-Content -Path $envFile -Value $lines -Encoding UTF8

$vars = @{}
Get-Content $envFile -Encoding UTF8 | Where-Object { $_ -match '^[A-Z_]+=' } | ForEach-Object {
    $k, $v = $_ -split '=', 2
    $vars[$k] = $v.Trim()
}

# 2. перезапуск бота
Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match "python" -and $_.CommandLine -match "bot\.main" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

$env:BOT_TOKEN = $vars["BOT_TOKEN"]
$env:WEBAPP_URL = $Url
$env:INTERNAL_API_KEY = $vars["INTERNAL_API_KEY"]
$env:API_URL = "http://localhost:8000"
$botDir = Join-Path $root "apps\bot"
$log = Join-Path $botDir "bot.log"
Remove-Item $log, "$log.err" -ErrorAction SilentlyContinue
Start-Process -FilePath (Join-Path $botDir ".venv\Scripts\python.exe") `
    -ArgumentList "-m", "bot.main" -WorkingDirectory $botDir -WindowStyle Hidden `
    -RedirectStandardOutput $log -RedirectStandardError "$log.err"

# 3. кнопка меню Mini App
$body = @{ menu_button = @{ type = "web_app"; text = "Levefit"; web_app = @{ url = $Url } } } |
    ConvertTo-Json -Depth 5
$result = Invoke-RestMethod "https://api.telegram.org/bot$($vars['BOT_TOKEN'])/setChatMenuButton" `
    -Method Post -ContentType "application/json; charset=utf-8" -Body $body -TimeoutSec 30
Write-Output "menu button set: $($result.ok); bot restarted with $Url"
