@echo off
echo ========================================
echo MixMaster - Stopping Backend Services
echo ========================================
echo.

echo Stopping Celery Worker...
taskkill /F /FI "WINDOWTITLE eq Celery Worker*" 2>nul
if errorlevel 1 (
    echo Celery Worker was not running
) else (
    echo Celery Worker stopped
)

echo.
echo Stopping Backend API...
taskkill /F /FI "WINDOWTITLE eq MixMaster API*" 2>nul
if errorlevel 1 (
    echo Backend API was not running
) else (
    echo Backend API stopped
)

echo.
echo Stopping Redis Server...
.\stop-redis.bat >nul 2>&1

echo.
echo ========================================
echo All Backend Services Stopped
echo ========================================
echo.
pause
