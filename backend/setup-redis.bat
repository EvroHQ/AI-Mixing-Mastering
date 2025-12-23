@echo off
echo ========================================
echo MixMaster - Redis Setup for Windows
echo ========================================
echo.

set REDIS_VERSION=3.0.504
set REDIS_URL=https://github.com/microsoftarchive/redis/releases/download/win-%REDIS_VERSION%/Redis-x64-%REDIS_VERSION%.zip
set INSTALL_DIR=%~dp0redis
set ZIP_FILE=%~dp0redis.zip

echo Step 1: Downloading Redis %REDIS_VERSION%...
echo.

if exist "%ZIP_FILE%" (
    echo Redis zip already downloaded
) else (
    powershell -Command "Invoke-WebRequest -Uri '%REDIS_URL%' -OutFile '%ZIP_FILE%'"
    if errorlevel 1 (
        echo Failed to download Redis
        pause
        exit /b 1
    )
    echo Download complete!
)

echo.
echo Step 2: Extracting Redis...
echo.

if exist "%INSTALL_DIR%" (
    echo Removing old Redis directory...
    rmdir /s /q "%INSTALL_DIR%"
)

powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%INSTALL_DIR%' -Force"
if errorlevel 1 (
    echo Failed to extract Redis
    pause
    exit /b 1
)
echo Extraction complete!

echo.
echo Step 3: Creating configuration...
echo.

(
echo port 6379
echo bind 127.0.0.1
echo protected-mode yes
echo timeout 0
echo databases 16
) > "%INSTALL_DIR%\redis.conf"

echo Configuration created!

echo.
echo Step 4: Creating start script...
echo.

(
echo @echo off
echo echo Starting Redis Server for MixMaster...
echo echo.
echo cd /d "%%~dp0redis"
echo start "Redis Server" redis-server.exe redis.conf
echo echo Redis Server started!
echo echo.
echo echo To stop Redis, close the Redis Server window
echo echo.
echo pause
) > "%~dp0start-redis.bat"

echo Start script created: start-redis.bat

echo.
echo Step 5: Creating stop script...
echo.

(
echo @echo off
echo echo Stopping Redis Server...
echo taskkill /F /IM redis-server.exe 2^>nul
echo if %%errorlevel%% == 0 ^(
echo     echo Redis Server stopped successfully!
echo ^) else ^(
echo     echo Redis Server was not running.
echo ^)
echo pause
) > "%~dp0stop-redis.bat"

echo Stop script created: stop-redis.bat

echo.
echo Step 6: Creating test script...
echo.

(
echo @echo off
echo echo Testing Redis connection...
echo echo.
echo cd /d "%%~dp0redis"
echo redis-cli.exe ping
echo if %%errorlevel%% == 0 ^(
echo     echo.
echo     echo Redis is running and responding!
echo ^) else ^(
echo     echo.
echo     echo Redis is not running. Start it with start-redis.bat
echo ^)
echo echo.
echo pause
) > "%~dp0test-redis.bat"

echo Test script created: test-redis.bat

echo.
echo Cleaning up...
del "%ZIP_FILE%"

echo.
echo ========================================
echo Redis Setup Complete!
echo ========================================
echo.
echo Installation Directory: %INSTALL_DIR%
echo.
echo Quick Start:
echo   1. Start Redis:  start-redis.bat
echo   2. Test Redis:   test-redis.bat
echo   3. Stop Redis:   stop-redis.bat
echo.
echo Redis will run on: localhost:6379
echo.
echo.

set /p START="Would you like to start Redis now? (Y/N): "
if /i "%START%"=="Y" (
    echo.
    echo Starting Redis...
    call start-redis.bat
    timeout /t 2 >nul
    echo Redis started!
)

echo.
echo Setup complete!
echo.
pause
