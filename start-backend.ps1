$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$EnvFile = Join-Path $BackendDir ".env"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
$LegacyVenvPython = Join-Path $BackendDir "venv\Scripts\python.exe"

if (-not (Test-Path (Join-Path $BackendDir "run.py"))) {
    throw "backend\run.py was not found. Run this script from the project root."
}

if (-not (Test-Path $EnvFile)) {
    Write-Host "backend\.env was not found. Configure it from backend\.env.example before using API features." -ForegroundColor Yellow
}

if (Test-Path $VenvPython) {
    $Python = $VenvPython
}
elseif (Test-Path $LegacyVenvPython) {
    $Python = $LegacyVenvPython
}
else {
    $Python = "python"
}

$env:PYTHONIOENCODING = "utf-8"

Push-Location $BackendDir
try {
    Write-Host "Starting backend: http://127.0.0.1:8000/" -ForegroundColor Green
    & $Python run.py
}
finally {
    Pop-Location
}
