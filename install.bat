@echo off
title FigCraft MCP Installer
echo ==================================================
echo       FigCraft Universal MCP Setup
echo ==================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python tidak ditemukan di PATH!
    echo Silakan install Python 3.8+ dari https://www.python.org/downloads/
    pause
    exit /b 1
)

python "%~dp0install.py"
echo.
pause
