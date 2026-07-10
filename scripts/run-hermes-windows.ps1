param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Missing virtualenv Python at $python"
}

Write-Host "Starting Hermes API on http://$HostAddress`:$Port" -ForegroundColor Cyan
Start-Process -FilePath $python -ArgumentList "-m uvicorn src.api.main:app --host $HostAddress --port $Port" -WorkingDirectory $repoRoot

Start-Sleep -Seconds 2
try {
    $health = Invoke-WebRequest -UseBasicParsing "http://$HostAddress`:$Port/health"
    Write-Host "Health check status: $($health.StatusCode)" -ForegroundColor Green
    Write-Host "OAuth status URL: http://$HostAddress`:$Port/auth/status" -ForegroundColor Green
}
catch {
    Write-Warning "API process started but health check failed: $($_.Exception.Message)"
    Write-Warning "Check whether another process already uses port $Port or if dependencies are missing."
}
