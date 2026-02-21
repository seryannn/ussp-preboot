@echo off
chcp 65001 >nul
title USSP Setup
color 0B
cls

if not exist "AppVersion" mkdir AppVersion
if not exist "src" mkdir src

if exist "UssP.exe" (
    copy /Y "UssP.exe" "AppVersion\UssP.exe" >nul
)

if exist "UssP.py" (
    copy /Y "UssP.py" "src\UssP.py" >nul
)

(
echo @echo off
echo title USSP Launcher
echo color 0B
echo set "EXE_PATH=AppVersion\UssP.exe"
echo set "PY_PATH=src\UssP.py"
echo if exist "%%EXE_PATH%%" (
echo     start "" "%%EXE_PATH%%"
echo     goto :end
echo )
echo if exist "%%PY_PATH%%" (
echo     python "%%PY_PATH%%"
echo     goto :end
echo )
echo echo USSP not found.
echo :end
) > launch_ussp.bat

if exist "requirements.txt" (
    pip install --upgrade pip
    pip install -r requirements.txt
)

exit /b 0
