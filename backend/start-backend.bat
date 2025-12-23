@echo off
echo ========================================
echo MixMaster - Starting Full Backend
echo ========================================
echo.

echo Checking Redis...
.\test-redis.bat >nul 2>&1
if errorlevel 1 (
    echo Redis is not running. Starting Redis...
    start "Redis Server" .\start-redis.bat
    timeout /t 3 >nul
) else (
    echo Redis is already running!
)

echo.
echo Starting Backend API...
start "MixMaster API" cmd /k "venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Waiting for API to start...
timeout /t 3 >nul

echo.
echo Starting Celery Worker...
start "Celery Worker" cmd /k "venv\Scripts\activate && celery -A celery_app worker --loglevel=info --pool=solo"

echo.
echo ========================================
echo Backend Started Successfully!
echo ========================================
echo.
echo Services running:
echo   - Redis Server:  localhost:6379
echo   - Backend API:   http://localhost:8000
echo   - Celery Worker: Running
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo To stop all services, close the terminal windows
echo or run: stop-backend.bat
echo.
pause
