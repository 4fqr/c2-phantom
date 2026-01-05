# Run C2 Phantom CLI
# This script helps you get started quickly

Write-Host "🔮 C2 Phantom - Quick Start" -ForegroundColor Cyan
Write-Host "=" * 50

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Check if package is installed
Write-Host "`nChecking C2 Phantom installation..." -ForegroundColor Yellow
$installed = pip show c2-phantom 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ C2 Phantom is installed" -ForegroundColor Green
} else {
    Write-Host "⚠ C2 Phantom not installed. Installing now..." -ForegroundColor Yellow
    pip install -e .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Installation complete" -ForegroundColor Green
    } else {
        Write-Host "✗ Installation failed" -ForegroundColor Red
        exit 1
    }
}

# Initialize if needed
Write-Host "`nChecking configuration..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.phantom\config.yaml"
if (Test-Path $configPath) {
    Write-Host "✓ Configuration exists" -ForegroundColor Green
} else {
    Write-Host "⚠ Configuration not found. Initializing..." -ForegroundColor Yellow
    phantom init
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Initialization complete" -ForegroundColor Green
    }
}

# Show banner
Write-Host ""
phantom --help

Write-Host "`n" + "=" * 50
Write-Host "Ready! Try these commands:" -ForegroundColor Cyan
Write-Host "  phantom --version" -ForegroundColor White
Write-Host "  phantom list" -ForegroundColor White
Write-Host "  phantom plugin list" -ForegroundColor White
Write-Host "  phantom connect https://example.com" -ForegroundColor White
Write-Host ""
