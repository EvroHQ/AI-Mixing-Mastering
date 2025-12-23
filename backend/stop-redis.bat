@echo off
echo Stopping Redis Server...
taskkill /F /IM redis-server.exe 2>nul
if %errorlevel% == 0 (
    echo Redis Server stopped successfully!
) else (
    echo Redis Server was not running.
)
pause
