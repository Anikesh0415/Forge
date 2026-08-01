@echo off
cd /d "%~dp0"
title FORGE AI - 1-Click Launcher

echo ===================================================
echo   FORGE AI OS - Booting System (Moondream2 Mode)
echo ===================================================
echo.
echo Launching Native AI Core...

start "FORGE AI Core Backend" ".\venv\Scripts\python.exe" forge_launcher.py

echo Boot sequence complete. Close this window anytime.
exit
