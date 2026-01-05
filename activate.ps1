# C2 Phantom Virtual Environment Activation Script
# Usage: .\activate.ps1

Write-Host "🔮 C2 Phantom - Activating Virtual Environment..." -ForegroundColor Cyan
Write-Host ""

# Activate the virtual environment
& "D:\c2-phantom\.venv\Scripts\Activate.ps1"

# Display welcome message
Write-Host "✅ Virtual Environment Activated!" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Package: c2-phantom v1.0.0" -ForegroundColor Yellow
Write-Host "🐍 Python: 3.13.7" -ForegroundColor Yellow
Write-Host "📁 Location: D:\c2-phantom" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Quick Commands:" -ForegroundColor Cyan
Write-Host "  phantom --help          # Show all commands" -ForegroundColor White
Write-Host "  phantom --version       # Show version" -ForegroundColor White
Write-Host "  phantom init            # Initialize configuration" -ForegroundColor White
Write-Host "  python -m pytest        # Run tests" -ForegroundColor White
Write-Host ""
Write-Host "💡 Note: The 'phantom' command is now available in your terminal!" -ForegroundColor Magenta
Write-Host ""
