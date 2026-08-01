@echo off
echo ===================================================
echo              Stopping Forge OS...
echo ===================================================
echo.

echo [1/3] Terminating llama-server (Moondream2)...
taskkill /F /IM llama-server.exe /T 2>NUL

echo [2/3] Terminating Forge Python Backend...
wmic process where "name='python.exe' and CommandLine like '%%server.py%%'" call terminate 2>NUL
wmic process where "name='python.exe' and CommandLine like '%%forge_launcher.py%%'" call terminate 2>NUL
taskkill /F /FI "WINDOWTITLE eq Forge OS*" /T 2>NUL

echo [3/3] Terminating any remaining Python instances tied to Forge...
REM If the above fails, we fallback to finding python processes running in the AIF_Project dir
for /f "tokens=2 delims=," %%a in ('wmic process where "name='python.exe' and ExecutablePath like '%%AIF_Project%%'" get ProcessId /format:csv 2^>NUL ^| findstr /r "[0-9]"') do (
    taskkill /F /PID %%a /T 2>NUL
)

echo.
echo ===================================================
echo              Forge OS Shutdown Complete!
echo ===================================================
pause
