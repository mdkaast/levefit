# Держит SSH-туннель localhost.run и при каждой смене адреса привязывает к нему бота
# (apply_tunnel_url.ps1). Бесплатные адреса меняются при переподключении, поэтому цикл бесконечный.
$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$apply = Join-Path $PSScriptRoot "apply_tunnel_url.ps1"
$dir = Join-Path $env:USERPROFILE "cloudflared-bin"
New-Item -ItemType Directory -Force $dir | Out-Null
$log = Join-Path $dir "ssh-tunnel.log"
$urlPattern = "https://[a-z0-9]+\.lhr\.life"
$applied = ""

function Get-CurrentUrl {
    if (-not (Test-Path $log)) { return "" }
    $text = (Get-Content $log -Raw -ErrorAction SilentlyContinue) -replace "\x1b\[[0-9;]*m", ""
    $found = @([regex]::Matches($text, $urlPattern) | ForEach-Object { $_.Value })
    if ($found.Count -gt 0) { return $found[$found.Count - 1] } else { return "" }
}

while ($true) {
    Remove-Item $log, "$log.err" -ErrorAction SilentlyContinue
    $ssh = Start-Process -FilePath "ssh.exe" -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $log -RedirectStandardError "$log.err" `
        -ArgumentList "-o", "StrictHostKeyChecking=accept-new", "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=3", "-o", "ExitOnForwardFailure=yes",
        "-R", "80:127.0.0.1:5173", "nokey@localhost.run"
    while (-not $ssh.HasExited) {
        $url = Get-CurrentUrl
        if ($url -and $url -ne $applied) {
            & $apply -Url $url
            $applied = $url
        }
        Start-Sleep -Seconds 5
    }
    Start-Sleep -Seconds 3
}

