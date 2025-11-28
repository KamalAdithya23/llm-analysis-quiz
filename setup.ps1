# Quick Setup Script for Windows
# Run this script to set up the project quickly

Write-Host "LLM Analysis Quiz - Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[1-9]") {
    Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.11+ required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($?) {
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($?) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Install Playwright browsers
Write-Host ""
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium
if ($?) {
    Write-Host "✓ Playwright browsers installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Playwright browsers" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
Write-Host ""
if (Test-Path .env) {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
} else {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Edit .env file with your actual values!" -ForegroundColor Red
    Write-Host "  - EMAIL: Your email address" -ForegroundColor Yellow
    Write-Host "  - SECRET: Your secret string" -ForegroundColor Yellow
    Write-Host "  - OPENAI_API_KEY: Your OpenAI API key" -ForegroundColor Yellow
    Write-Host "  - API_ENDPOINT_URL: Your deployed endpoint URL" -ForegroundColor Yellow
    Write-Host "  - GITHUB_REPO_URL: Your GitHub repository URL" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path downloads | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Run: uvicorn src.api.server:app --reload" -ForegroundColor White
Write-Host "3. Test with: curl -X POST http://localhost:8000/health" -ForegroundColor White
Write-Host ""
