@echo off
title Intent Engine Health Check
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo.
uv run engine health
echo.
pause
