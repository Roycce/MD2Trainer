@echo off
title Minecraft Dungeons II - Standalone Native Trainer
cd /d "%~dp0"

:: Request Administrator privileges (required for WindowsApps / WinGDK memory writes)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Requesting Administrator privileges to attach to game process...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
    exit /b
)

python --version >nul 2>nul
if %errorlevel% equ 0 (
    python trainer_gui.py
    goto :end
)

py -3 --version >nul 2>nul
if %errorlevel% equ 0 (
    py -3 trainer_gui.py
    goto :end
)

echo [ERROR] Python was not found in your system PATH.
echo Please install 64-bit Python 3.10+ from python.org and ensure "Add Python to PATH" is checked.
echo.
pause
exit /b 1

:end
set "trainer_exit=%errorlevel%"
if not "%trainer_exit%"=="0" (
    echo.
    echo [ERROR] The trainer could not run. See the error above.
    pause
)
exit /b %trainer_exit%
