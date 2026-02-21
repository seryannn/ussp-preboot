@echo off
chcp 65001 >nul
title USSP Launcher
color 0B

set "EXE_PATH=AppVersion\UssP.exe"
set "PY_PATH=src\UssP.py"

cls
echo.
echo USSP SAFE APP LAUNCHER
echo.
echo          Initializing environment...
timeout /t 1 >nul

echo.
echo   [*] Checking executable version...
if exist "%EXE_PATH%" (
    color 0A
    echo   [OK] Binary version detected
    echo.
    echo   Launching USSP (EXE)...
    timeout /t 1 >nul
    start "" "%EXE_PATH%"
    goto :success
)

color 0E
echo   [WARN] Executable not found
echo.
echo   [*] Checking Python version...
if exist "%PY_PATH%" (
    echo   [OK] Python source detected
    echo.
    echo   Launching USSP (Python)...
    timeout /t 1 >nul
    python "%PY_PATH%"
    goto :success
)

color 0C
echo.
echo   [ERROR] USSP not found
echo.
echo   Checked paths:
echo     - AppVersion\UssP.exe
echo     - src\UssP.py
echo.
echo   Please verify your installation.
pause
exit /b 1

:succes
color 0A
echo.
echo   ╔════════════════════════════════════╗
echo   ║   USSP LAUNCHED SUCCESSFULLY        ║
echo   ╚════════════════════════════════════╝
exit /b 0
