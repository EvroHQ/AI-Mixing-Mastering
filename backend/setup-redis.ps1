# MixMaster - Redis Setup Script for Windows
# This script downloads and configures Redis for the MixMaster backend

Write-Host "🎵 MixMaster - Redis Setup for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$redisVersion = "3.0.504"
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-$redisVersion/Redis-x64-$redisVersion.zip"
$installDir = "$PSScriptRoot\redis"
$zipFile = "$PSScriptRoot\redis.zip"

# Step 1: Download Redis
Write-Host "📥 Step 1: Downloading Redis $redisVersion..." -ForegroundColor Yellow

try {
    if (Test-Path $zipFile) {
        Write-Host "   ✓ Redis zip already downloaded" -ForegroundColor Green
    } else {
        Invoke-WebRequest -Uri $redisUrl -OutFile $zipFile
        Write-Host "   ✓ Download complete" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Failed to download Redis: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Extract Redis
Write-Host ""
Write-Host "📦 Step 2: Extracting Redis..." -ForegroundColor Yellow

try {
    if (Test-Path $installDir) {
        Write-Host "   ℹ Redis directory already exists, removing..." -ForegroundColor Gray
        Remove-Item -Path $installDir -Recurse -Force
    }
    
    Expand-Archive -Path $zipFile -DestinationPath $installDir -Force
    Write-Host "   ✓ Extraction complete" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to extract Redis: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Create Redis configuration
Write-Host ""
Write-Host "⚙️  Step 3: Creating Redis configuration..." -ForegroundColor Yellow

$redisConf = @"
# Redis Configuration for MixMaster
port 6379
bind 127.0.0.1
protected-mode yes
timeout 0
tcp-keepalive 300
daemonize no
supervised no
loglevel notice
databases 16
save 900 1
save 300 10
save 60 10000
"@

try {
    $redisConf | Out-File -FilePath "$installDir\redis.conf" -Encoding ASCII
    Write-Host "   ✓ Configuration created" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to create configuration: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Create start script
Write-Host ""
Write-Host "📝 Step 4: Creating start script..." -ForegroundColor Yellow

$startScript = @"
@echo off
echo Starting Redis Server for MixMaster...
echo.
cd /d "%~dp0redis"
start "Redis Server" redis-server.exe redis.conf
echo Redis Server started!
echo.
echo To stop Redis, close the Redis Server window or press Ctrl+C
echo.
pause
"@

try {
    $startScript | Out-File -FilePath "$PSScriptRoot\start-redis.bat" -Encoding ASCII
    Write-Host "   ✓ Start script created: start-redis.bat" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to create start script: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Create stop script
Write-Host ""
Write-Host "📝 Step 5: Creating stop script..." -ForegroundColor Yellow

$stopScript = @"
@echo off
echo Stopping Redis Server...
taskkill /F /IM redis-server.exe 2>nul
if %errorlevel% == 0 (
    echo Redis Server stopped successfully!
) else (
    echo Redis Server was not running.
)
pause
"@

try {
    $stopScript | Out-File -FilePath "$PSScriptRoot\stop-redis.bat" -Encoding ASCII
    Write-Host "   ✓ Stop script created: stop-redis.bat" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to create stop script: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Create test script
Write-Host ""
Write-Host "📝 Step 6: Creating test script..." -ForegroundColor Yellow

$testScript = @"
@echo off
echo Testing Redis connection...
echo.
cd /d "%~dp0redis"
redis-cli.exe ping
if %errorlevel% == 0 (
    echo.
    echo ✓ Redis is running and responding!
) else (
    echo.
    echo ✗ Redis is not running. Please start it first with start-redis.bat
)
echo.
pause
"@

try {
    $testScript | Out-File -FilePath "$PSScriptRoot\test-redis.bat" -Encoding ASCII
    Write-Host "   ✓ Test script created: test-redis.bat" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to create test script: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Write-Host ""
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
Remove-Item -Path $zipFile -Force
Write-Host "   ✓ Cleanup complete" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Redis Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Installation Directory: $installDir" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Quick Start:" -ForegroundColor Yellow
Write-Host "   1. Start Redis:  .\start-redis.bat" -ForegroundColor White
Write-Host "   2. Test Redis:   .\test-redis.bat" -ForegroundColor White
Write-Host "   3. Stop Redis:   .\stop-redis.bat" -ForegroundColor White
Write-Host ""
Write-Host "💡 Redis will run on: localhost:6379" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "   1. Run .\start-redis.bat to start Redis" -ForegroundColor White
Write-Host "   2. Configure your backend .env file" -ForegroundColor White
Write-Host "   3. Start the backend API and Celery worker" -ForegroundColor White
Write-Host ""

# Ask if user wants to start Redis now
$response = Read-Host "Would you like to start Redis now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Starting Redis..." -ForegroundColor Yellow
    Start-Process -FilePath "$PSScriptRoot\start-redis.bat"
    Start-Sleep -Seconds 2
    Write-Host "✓ Redis started!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green
