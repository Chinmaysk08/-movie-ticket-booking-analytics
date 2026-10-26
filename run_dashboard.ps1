# Starts the Streamlit dashboard in the background and opens the browser.
# Usage:  .\run_dashboard.ps1
# Stop:   .\run_dashboard.ps1 -Stop

param([switch]$Stop)

$project = "D:\chinmay\movie-ticket-booking-analytics"
$venv    = "D:\venvs\cinema"
$port    = 8501

if ($Stop) {
    Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Dashboard stopped."
    return
}

# Stop any previous instance
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

$env:PYTHONPATH = Join-Path $project "src"
$env:STREAMLIT_SERVER_ADDRESS = "127.0.0.1"
$env:STREAMLIT_SERVER_PORT = "$port"
$env:STREAMLIT_SERVER_HEADLESS = "true"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"

$logDir = Join-Path $project "reports\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$proc = Start-Process -FilePath (Join-Path $venv "Scripts\streamlit.exe") `
    -ArgumentList @("run", "dashboard/app.py") `
    -WorkingDirectory $project `
    -RedirectStandardOutput (Join-Path $logDir "streamlit.out.log") `
    -RedirectStandardError  (Join-Path $logDir "streamlit.err.log") `
    -WindowStyle Hidden -PassThru

Write-Host "Starting dashboard (PID $($proc.Id))..."
Start-Sleep -Seconds 10

try {
    $r = Invoke-WebRequest "http://127.0.0.1:$port" -UseBasicParsing -TimeoutSec 15
    Write-Host "Dashboard ready: http://127.0.0.1:$port  (HTTP $($r.StatusCode))"
    Start-Process "http://127.0.0.1:$port"
} catch {
    Write-Host "Dashboard did not start. Check reports\logs\streamlit.err.log"
}
