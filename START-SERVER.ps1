#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start C2-Phantom Go server with production-ready configuration
.DESCRIPTION
    Launches the Go C2 server with database connectivity, Redis, TLS, and security hardening
.EXAMPLE
    .\START-SERVER.ps1
#>

param(
    [string]$DatabaseURL = "memory",
    [string]$RedisURL = "",
    [int]$HTTPPort = 8080,
    [int]$HTTPSPort = 443,
    [string]$LogLevel = "info",
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"

Write-Host "[*] Starting C2-Phantom Server..." -ForegroundColor Cyan
Write-Host ""

# Check if server binary exists
$ServerPath = Join-Path $PSScriptRoot "server"
if (-not (Test-Path $ServerPath)) {
    Write-Host "[!] Server directory not found: $ServerPath" -ForegroundColor Red
    exit 1
}

# Set environment variables
$env:DATABASE_URL = $DatabaseURL
$env:REDIS_URL = $RedisURL
$env:HTTP_PORT = $HTTPPort
$env:HTTPS_PORT = $HTTPSPort
$env:LOG_LEVEL = $LogLevel
$env:MAX_AGENTS = "10000"

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  Database: $DatabaseURL"
if ($RedisURL -ne "") {
    Write-Host "  Redis: $RedisURL"
} else {
    Write-Host "  Redis: disabled (using in-memory queues)"
}
Write-Host "  HTTP Port: $HTTPPort"
Write-Host "  HTTPS Port: $HTTPSPort"
Write-Host "  Log Level: $LogLevel"
Write-Host ""

# Build if needed or forced
$BinaryPath = Join-Path $ServerPath "c2-server.exe"
if ($Rebuild -and (Test-Path $BinaryPath)) {
    Write-Host "[+] Rebuilding Go server (forced)..." -ForegroundColor Yellow
    Remove-Item $BinaryPath -Force
}

if (-not (Test-Path $BinaryPath)) {
    Write-Host "[+] Building Go server..." -ForegroundColor Yellow
    Push-Location $ServerPath
    try {
        # Sync dependencies and update go.sum
        go mod tidy
        if ($LASTEXITCODE -ne 0) {
            throw "Go mod tidy failed"
        }
        
        # Build with pure Go (no CGO/gcc needed)
        $env:CGO_ENABLED = "0"
        go build -tags modernc_sqlite -o c2-server.exe -ldflags="-s -w" main.go
        if ($LASTEXITCODE -ne 0) {
            throw "Go build failed"
        }
    } finally {
        Pop-Location
    }
}

Write-Host "[+] Starting server..." -ForegroundColor Green
Write-Host ""

# Start server
Push-Location $ServerPath
try {
    & ./c2-server.exe
} finally {
    Pop-Location
}
