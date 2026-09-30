@echo off
title Minecraft Dungeons II - Standalone Native Trainer
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% equ 0 (
    python trainer_gui.py
    goto :end
)

where py >nul 2>nul
if %errorlevel% equ 0 (
    py trainer_gui.py
    goto :end
)

echo [ERROR] Python was not found in your system PATH.
echo Please install Python 3.10+ from python.org and ensure "Add Python to PATH" is checked.
echo.
pause

:end
