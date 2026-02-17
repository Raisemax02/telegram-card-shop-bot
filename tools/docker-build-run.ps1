<#
.SYNOPSIS
    Build and run the Telegram Bot Docker container.
.DESCRIPTION
    This script builds the Docker image and starts the container
    using docker compose. Supports build, run, rebuild, stop, logs, and status modes.
.PARAMETER Action
    The action to perform: build, run, rebuild, stop, logs, status.
    Default: rebuild (build + run).
.EXAMPLE
    .\docker-build-run.ps1 -Action rebuild
    .\docker-build-run.ps1 -Action logs
    .\docker-build-run.ps1 -Action status
#>

param(
    [ValidateSet("build", "run", "rebuild", "stop", "logs", "status")]
    [string]$Action = "rebuild"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ProjectRoot
try {
    switch ($Action) {
        "build" {
            Write-Host "[BUILD] Building Docker image..." -ForegroundColor Cyan
            docker compose build --no-cache
            if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
            Write-Host "[OK] Build completed." -ForegroundColor Green
        }
        "run" {
            Write-Host "[RUN] Starting container..." -ForegroundColor Cyan
            docker compose up -d
            if ($LASTEXITCODE -ne 0) { throw "Docker run failed" }
            Write-Host "[OK] Container started." -ForegroundColor Green
            docker compose ps
        }
        "rebuild" {
            Write-Host "[REBUILD] Building and starting..." -ForegroundColor Cyan
            docker compose down 2>$null
            docker compose up -d --build
            if ($LASTEXITCODE -ne 0) { throw "Docker rebuild failed" }
            Write-Host "[OK] Container rebuilt and started." -ForegroundColor Green
            docker compose ps
        }
        "stop" {
            Write-Host "[STOP] Stopping container..." -ForegroundColor Yellow
            docker compose down
            Write-Host "[OK] Container stopped." -ForegroundColor Green
        }
        "logs" {
            Write-Host "[LOGS] Showing live logs (Ctrl+C to exit)..." -ForegroundColor Cyan
            docker compose logs -f bot
        }
        "status" {
            Write-Host "[STATUS] Container status:" -ForegroundColor Cyan
            docker compose ps
            Write-Host ""
            Write-Host "[RESOURCES] Resource usage:" -ForegroundColor Cyan
            docker stats telegram-bot --no-stream 2>$null
        }
    }
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}
