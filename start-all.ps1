$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendScript = Join-Path $RootDir "start-frontend.ps1"
$BackendScript = Join-Path $RootDir "start-backend.ps1"

Write-Host "Starting backend and frontend development servers..." -ForegroundColor Green

function Test-ListeningPort {
    param([int]$Port)

    $pattern = ":$Port\s+.*LISTENING"
    return [bool](netstat -ano | Select-String -Pattern $pattern)
}

function Wait-ForHttp {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
            Start-Sleep -Milliseconds 500
        }
    }

    return $false
}

if (Test-ListeningPort -Port 8000) {
    Write-Host "Backend port 8000 is already in use. Skipping backend startup." -ForegroundColor Yellow
}
else {
    Start-Process powershell.exe -ArgumentList @(
        "-NoProfile",
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $BackendScript
    ) -WorkingDirectory $RootDir
}

if (Test-ListeningPort -Port 5173) {
    Write-Host "Frontend port 5173 is already in use. Skipping frontend startup." -ForegroundColor Yellow
}
else {
    Start-Process powershell.exe -ArgumentList @(
        "-NoProfile",
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $FrontendScript
    ) -WorkingDirectory $RootDir
}

$backendReady = Wait-ForHttp -Url "http://127.0.0.1:8000/health" -TimeoutSeconds 20
$frontendReady = Wait-ForHttp -Url "http://127.0.0.1:5173/" -TimeoutSeconds 30

if ($backendReady) {
    Write-Host "Backend ready:  http://127.0.0.1:8000/" -ForegroundColor Green
}
else {
    Write-Host "Backend did not become ready. Check the backend window for errors." -ForegroundColor Yellow
}

if ($frontendReady) {
    Write-Host "Frontend ready: http://127.0.0.1:5173/" -ForegroundColor Green
    Start-Process "http://127.0.0.1:5173/"
}
else {
    throw "Frontend did not become ready. Check the frontend window for errors."
}
