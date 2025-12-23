@echo off
echo Starting Redis Server for MixMaster...
echo.
cd /d "%~dp0redis"
start "Redis Server" redis-server.exe redis.conf
echo Redis Server started!
echo.
echo To stop Redis, close the Redis Server window
echo.
pause
