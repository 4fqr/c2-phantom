#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build all C2-Phantom components on Windows
.DESCRIPTION
    Builds C core, Rust agent, and Go server without Make
.EXAMPLE
    .\BUILD-ALL.ps1
#>

param(
    [switch]$SkipC,
    [switch]$SkipRust,
    [switch]$SkipGo,
    [switch]$Release
)

$ErrorActionPreference = "Stop"

Write-Host "🔮 Building C2-Phantom Components..." -ForegroundColor Cyan
Write-Host ""

$BuildSuccess = @()
$BuildFailed = @()

# ============================================================================
# Build C Core
# ============================================================================
if (-not $SkipC) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "🔨 Building C Core..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        # Check for CMake
        if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
            Write-Host "⚠️  CMake not found - skipping C core build" -ForegroundColor Yellow
            Write-Host "   Install: choco install cmake" -ForegroundColor DarkGray
        } else {
            New-Item -ItemType Directory -Force -Path "build" | Out-Null
            Push-Location "build"
            try {
                cmake -G "Visual Studio 17 2022" -A x64 ..
                cmake --build . --config Release
                Write-Host "✓ C core built successfully" -ForegroundColor Green
                $BuildSuccess += "C Core"
            } catch {
                Write-Host "❌ C core build failed: $_" -ForegroundColor Red
                $BuildFailed += "C Core"
            } finally {
                Pop-Location
            }
        }
    } catch {
        Write-Host "❌ C core setup failed: $_" -ForegroundColor Red
        $BuildFailed += "C Core"
    }
    Write-Host ""
}

# ============================================================================
# Build Rust Agent
# ============================================================================
if (-not $SkipRust) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "🦀 Building Rust Agent..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        # Check for Cargo
        if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
            Write-Host "⚠️  Cargo not found - skipping Rust agent build" -ForegroundColor Yellow
            Write-Host "   Install: https://rustup.rs/" -ForegroundColor DarkGray
        } else {
            Push-Location "agent"
            try {
                if ($Release) {
                    cargo build --release
                    Write-Host "✓ Rust agent built: target/release/agent.exe" -ForegroundColor Green
                } else {
                    cargo build
                    Write-Host "✓ Rust agent built: target/debug/agent.exe" -ForegroundColor Green
                }
                $BuildSuccess += "Rust Agent"
            } catch {
                Write-Host "❌ Rust agent build failed: $_" -ForegroundColor Red
                $BuildFailed += "Rust Agent"
            } finally {
                Pop-Location
            }
        }
    } catch {
        Write-Host "❌ Rust agent setup failed: $_" -ForegroundColor Red
        $BuildFailed += "Rust Agent"
    }
    Write-Host ""
}

# ============================================================================
# Build Go Server
# ============================================================================
if (-not $SkipGo) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "🐹 Building Go Server..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        # Check for Go
        if (-not (Get-Command go -ErrorAction SilentlyContinue)) {
            Write-Host "⚠️  Go not found - skipping server build" -ForegroundColor Yellow
            Write-Host "   Install: choco install golang" -ForegroundColor DarkGray
        } else {
            Push-Location "server"
            try {
                go mod download
                if ($Release) {
                    go build -ldflags="-s -w" -o "c2-server.exe" main.go
                } else {
                    go build -o "c2-server.exe" main.go
                }
                Write-Host "✓ Go server built: server/c2-server.exe" -ForegroundColor Green
                $BuildSuccess += "Go Server"
            } catch {
                Write-Host "❌ Go server build failed: $_" -ForegroundColor Red
                $BuildFailed += "Go Server"
            } finally {
                Pop-Location
            }
        }
    } catch {
        Write-Host "❌ Go server setup failed: $_" -ForegroundColor Red
        $BuildFailed += "Go Server"
    }
    Write-Host ""
}

# ============================================================================
# Summary
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "📊 Build Summary" -ForegroundColor Cyan
Write-Host ""

if ($BuildSuccess.Count -gt 0) {
    Write-Host "✓ Successfully built:" -ForegroundColor Green
    foreach ($component in $BuildSuccess) {
        Write-Host "  • $component" -ForegroundColor Green
    }
    Write-Host ""
}

if ($BuildFailed.Count -gt 0) {
    Write-Host "❌ Failed to build:" -ForegroundColor Red
    foreach ($component in $BuildFailed) {
        Write-Host "  • $component" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}

Write-Host "✓ All builds completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Install Python package: pip install -e ." -ForegroundColor White
Write-Host "  2. Start server: .\START-SERVER.ps1" -ForegroundColor White
Write-Host "  3. Use CLI: python phantom.py --help" -ForegroundColor White
Write-Host ""
