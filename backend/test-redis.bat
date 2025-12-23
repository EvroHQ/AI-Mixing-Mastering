@echo off
echo Testing Redis connection...
echo.
cd /d "%~dp0redis"
redis-cli.exe ping
if %errorlevel% == 0 (
    echo.
    echo Redis is running and responding!
) else (
    echo.
    echo Redis is not running. Start it with start-redis.bat
)
echo.
pause
