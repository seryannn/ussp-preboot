@echo off
chcp 65001 >nul
title USSP Command Launcher
color 1E
cls
echo This isn't a real shell like the Windows shell; it's a custom shell designed for my UssP project! If you encounter any bugs, please contact the owner through the GitHub issues so they can be fixed as quickly as possible.
echo.

:prompt
set "userpath=C:\Users\%USERNAME%\UssP"
set /p "cmd=US %userpath% > "

if /i "%cmd%"=="" goto prompt
if /i "%cmd%"=="help" goto help
if /i "%cmd%"=="clear" goto clear
if /i "%cmd%"=="exit" exit /b 0
if /i "%cmd%"=="launcher" goto launcher
if /i "%cmd%"=="python" goto python
if /i "%cmd%"=="exe" goto exe
if /i "%cmd:~0,6%"=="runas " goto runas
if /i "%cmd%"=="github" goto github
if /i "%cmd%"=="docs" goto docs

echo [ERROR] Unknown command: %cmd%
goto prompt

:help
echo ============================================
echo USSP COMMAND LAUNCHER
echo ============================================
echo help        - Show this help
echo launcher    - Launch USSP Launcher
echo python      - Launch Python USSP script
echo exe         - Launch UssP.exe
echo runas <path> - Run file as admin
echo github      - Open USSP GitHub repo
echo docs        - Open README.md
echo clear       - Clear screen
echo exit        - Exit shell
echo ============================================
goto prompt

:clear
cls
echo This isn't a real shell like the Windows shell; it's a custom shell designed for my UssP project! If you encounter any bugs, please contact the owner through the GitHub issues so they can be fixed as quickly as possible.
echo.
goto prompt

:launcher
if exist "launch_ussp.bat" start "" "launch_ussp.bat" || echo [ERROR] Launcher not found.
goto prompt

:python
if exist "src\UssP.py" python "src\UssP.py" || echo [ERROR] Python script not found.
goto prompt

:exe
if exist "AppVersion\UssP.exe" start "" "AppVersion\UssP.exe" || echo [ERROR] EXE not found.
goto prompt

:runas
for /f "tokens=2*" %%a in ("%cmd%") do set "adminpath=%%b"
if exist "%adminpath%" (
    powershell -Command "Start-Process '%adminpath%' -Verb RunAs"
) else (
    echo [ERROR] File not found: %adminpath%
)
goto prompt

:github
start https://github.com/seryannn/ussp-preboot/
goto prompt

:docs
if exist "README.md" start "" "README.md" || echo [ERROR] README.md not found.
goto prompt
