@echo off
title Intent Engine Health Check
cd /d "%~dp0"
echo.
echo  Pulling latest changes...
git pull --rebase origin main 2>nul
echo.
uv run engine health
echo.
pause
