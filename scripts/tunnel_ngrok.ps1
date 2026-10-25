# Запускает ngrok на закреплённом бесплатном домене и привязывает к нему бота.
# Нужно: ngrok в %USERPROFILE%\ngrok-bin, токен (`ngrok config add-authtoken`), NGROK_DOMAIN в apps\api\.env.
# Агент ngrok не должен ходить через HTTP-прокси (это платная функция), поэтому прокси-переменные снимаем.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $root "apps\api\.env"
$domain = (Get-Content $envFile -Encoding UTF8 | Where-Object { $_ -like "NGROK_DOMAIN=*" } | Select-Object -First 1) -replace "^NGROK_DOMAIN=", ""
if (-not $domain) { throw "NGROK_DOMAIN не задан в $envFile" }

Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
foreach ($n in "HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy", "ALL_PROXY", "all_proxy") {
    Remove-Item "Env:$n" -ErrorAction SilentlyContinue
}
$dir = Join-Path $env:USERPROFILE "ngrok-bin"
$log = Join-Path $dir "ngrok.log"
Remove-Item $log, "$log.err" -ErrorAction SilentlyContinue
Start-Process -FilePath (Join-Path $dir "ngrok.exe") -WindowStyle Hidden `
    -ArgumentList "http", "--url=$domain", "127.0.0.1:5173", "--log=stdout", "--log-format=json" `
    -RedirectStandardOutput $log -RedirectStandardError "$log.err"
Start-Sleep -Seconds 10
$failed = Get-Content $log -ErrorAction SilentlyContinue | Where-Object { $_ -match "ERR_NGROK" } | Select-Object -First 1
if ($failed) { throw "ngrok не подключился: $failed" }
Write-Output "ngrok запущен на https://$domain"
