$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $RootDir "frontend"

if (-not (Test-Path (Join-Path $FrontendDir "package.json"))) {
    throw "frontend\package.json was not found. Run this script from the project root."
}

Push-Location $FrontendDir
try {
    if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
        Write-Host "Frontend dependencies are missing. Running npm install..." -ForegroundColor Yellow
        npm.cmd install
    }

    Write-Host "Starting frontend: http://127.0.0.1:5173/" -ForegroundColor Green
    npm.cmd run dev -- --host 127.0.0.1 --strictPort
}
finally {
    Pop-Location
}
