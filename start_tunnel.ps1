# Belvo Synapse - Cloudflare Tunnel Launcher
param (
    [int]$Port = 8000,
    [string]$Token = ""
)

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Starting Belvo Synapse Cloudflare Tunnel   " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$PythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

if ($Token) {
    & $PythonExe tunnel.py --port $Port --token $Token
} else {
    & $PythonExe tunnel.py --port $Port
}
