# Останавливает стенд, запущенный через dev_up.ps1.
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "tunnel_supervisor|bot\.main|uvicorn app\.main|vite" -or $_.Name -eq "ssh.exe" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Write-Output "stopped"
