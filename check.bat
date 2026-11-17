@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo   FigCraft Universal MCP Bridge - Health Check
echo ===================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Python executable was not found in your system PATH.
    echo Please install Python 3.8+ and ensure "Add python.exe to PATH" is checked.
    echo.
    pause
    exit /b 1
)

python check.py

echo.
pause
