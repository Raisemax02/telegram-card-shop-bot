<#
.SYNOPSIS
    Maintenance utilities for the Telegram Bot.
.DESCRIPTION
    Provides database backup, cleanup, log management,
    and health check utilities for the bot.
.PARAMETER Action
    The action to perform: backup, cleanup, health, reset-logs, db-info.
    Default: health.
.EXAMPLE
    .\maintenance.ps1 -Action health
    .\maintenance.ps1 -Action backup
    .\maintenance.ps1 -Action cleanup
    .\maintenance.ps1 -Action db-info
#>

param(
    [ValidateSet("backup", "cleanup", "health", "reset-logs", "db-info")]
    [string]$Action = "health"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"
$LogsDir = Join-Path $ProjectRoot "logs"
$BackupDir = Join-Path $DataDir "backups"
$DbFile = Join-Path $DataDir "negozio.json"

switch ($Action) {
    "backup" {
        Write-Host "[BACKUP] Creating database backup..." -ForegroundColor Cyan
        if (-not (Test-Path $DbFile)) {
            Write-Host "[ERROR] Database file not found: $DbFile" -ForegroundColor Red
            exit 1
        }
        if (-not (Test-Path $BackupDir)) {
            New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        }
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = Join-Path $BackupDir "negozio_backup_${timestamp}.json"
        Copy-Item $DbFile $backupFile
        Write-Host "[OK] Backup created: $backupFile" -ForegroundColor Green
    }

    "cleanup" {
        Write-Host "[CLEANUP] Removing old backups and caches..." -ForegroundColor Cyan

        # Remove old backups (keep last 5)
        if (Test-Path $BackupDir) {
            $backups = Get-ChildItem $BackupDir -Filter "negozio_backup_*.json" |
                Sort-Object Name -Descending
            $toRemove = $backups | Select-Object -Skip 5
            if ($toRemove) {
                $toRemove | Remove-Item -Force
                Write-Host "[OK] Removed $($toRemove.Count) old backup(s)." -ForegroundColor Green
            }
            else {
                Write-Host "[OK] No old backups to remove." -ForegroundColor Green
            }
        }

        # Remove __pycache__ directories
        $caches = Get-ChildItem $ProjectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
        if ($caches) {
            $caches | Remove-Item -Recurse -Force
            Write-Host "[OK] Removed $($caches.Count) __pycache__ directory(ies)." -ForegroundColor Green
        }

        # Remove .egg-info directories
        $eggInfo = Get-ChildItem $ProjectRoot -Recurse -Directory -Filter "*.egg-info" -ErrorAction SilentlyContinue
        if ($eggInfo) {
            $eggInfo | Remove-Item -Recurse -Force
            Write-Host "[OK] Removed egg-info directories." -ForegroundColor Green
        }

        Write-Host "[DONE] Cleanup completed." -ForegroundColor Green
    }

    "health" {
        Write-Host "[HEALTH] Bot Health Check" -ForegroundColor Cyan
        Write-Host "=========================" -ForegroundColor Cyan

        # Check database
        if (Test-Path $DbFile) {
            $dbSize = (Get-Item $DbFile).Length
            Write-Host "[OK] Database: $([math]::Round($dbSize / 1KB, 2)) KB" -ForegroundColor Green
        }
        else {
            Write-Host "[WARN] Database not found" -ForegroundColor Yellow
        }

        # Check backups
        if (Test-Path $BackupDir) {
            $backupCount = (Get-ChildItem $BackupDir -Filter "*.json").Count
            Write-Host "[OK] Backups: $backupCount file(s)" -ForegroundColor Green
        }
        else {
            Write-Host "[WARN] No backup directory" -ForegroundColor Yellow
        }

        # Check logs
        if (Test-Path $LogsDir) {
            $logFiles = Get-ChildItem $LogsDir -Filter "*.log" -ErrorAction SilentlyContinue
            if ($logFiles) {
                $totalSize = ($logFiles | Measure-Object -Property Length -Sum).Sum
                Write-Host "[OK] Logs: $($logFiles.Count) file(s), $([math]::Round($totalSize / 1KB, 2)) KB" -ForegroundColor Green
            }
            else {
                Write-Host "[INFO] Log directory exists but no log files yet" -ForegroundColor Cyan
            }
        }
        else {
            Write-Host "[INFO] No log directory yet" -ForegroundColor Cyan
        }

        # Check Docker container
        $container = docker ps --filter "name=telegram-bot" --format "{{.Status}}" 2>$null
        if ($container) {
            Write-Host "[OK] Docker: $container" -ForegroundColor Green
        }
        else {
            Write-Host "[WARN] Docker container not running" -ForegroundColor Yellow
        }

        # Check .env file
        $envFile = Join-Path $ProjectRoot ".env"
        if (Test-Path $envFile) {
            Write-Host "[OK] .env file present" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] .env file missing!" -ForegroundColor Red
        }
    }

    "reset-logs" {
        Write-Host "[LOGS] Resetting log files..." -ForegroundColor Yellow
        if (Test-Path $LogsDir) {
            $removed = Get-ChildItem $LogsDir -Filter "*.log" -ErrorAction SilentlyContinue
            if ($removed) {
                $removed | Remove-Item -Force
                Write-Host "[OK] Removed $($removed.Count) log file(s)." -ForegroundColor Green
            }
            else {
                Write-Host "[OK] No log files to remove." -ForegroundColor Green
            }
        }
        else {
            Write-Host "[OK] No log directory to clean." -ForegroundColor Green
        }
    }

    "db-info" {
        Write-Host "[DATABASE] Database Information" -ForegroundColor Cyan
        Write-Host "===============================" -ForegroundColor Cyan
        if (Test-Path $DbFile) {
            $content = Get-Content $DbFile -Raw | ConvertFrom-Json
            $defaultTable = $content._default
            if ($defaultTable) {
                $cardCount = ($defaultTable.PSObject.Properties | Measure-Object).Count
                Write-Host "[INFO] Total cards: $cardCount" -ForegroundColor Cyan
                foreach ($prop in $defaultTable.PSObject.Properties) {
                    $card = $prop.Value
                    $reviewCount = 0
                    if ($card.reviews) { $reviewCount = $card.reviews.Count }
                    Write-Host "  [$($prop.Name)] $($card.title) ($($card.category)) - $reviewCount review(s)" -ForegroundColor White
                }
            }
            else {
                Write-Host "[INFO] Database is empty." -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "[ERROR] Database file not found." -ForegroundColor Red
        }
    }
}
