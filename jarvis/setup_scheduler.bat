@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  SaaSpare Jarvis — Windows Task Scheduler Setup
REM  Run this once as Administrator to schedule daily briefings
REM  Usage: Right-click → "Run as administrator"
REM ═══════════════════════════════════════════════════════════════════

SET REPO=C:\Users\smith\intent-engine
SET UV=uv
SET PYTHON_SCRIPT=%REPO%\jarvis\daily_brief.py

echo Setting up SaaSpare Jarvis daily brief at 7:00 AM...

REM Delete existing task if present
schtasks /delete /tn "SaaSpare-Jarvis-DailyBrief" /f 2>nul

REM Create daily brief task at 7 AM
schtasks /create ^
  /tn "SaaSpare-Jarvis-DailyBrief" ^
  /tr "%UV% run python %PYTHON_SCRIPT%" ^
  /sc daily ^
  /st 07:00 ^
  /sd 01/01/2026 ^
  /ru "%USERNAME%" ^
  /rl highest ^
  /f

echo.
echo Daily brief scheduled for 7:00 AM every day.
echo Output written to: %REPO%\seo\reports\daily-brief.md
echo.

REM Optional: schedule wake listener to start at logon (uncomment to enable)
REM schtasks /create ^
REM   /tn "SaaSpare-Jarvis-VoiceListener" ^
REM   /tr "%UV% run python %REPO%\jarvis\wake_listener.py" ^
REM   /sc onlogon ^
REM   /ru "%USERNAME%" ^
REM   /f
REM echo Voice listener scheduled to start at logon.

echo.
echo To run the daily brief right now:
echo   uv run python jarvis\daily_brief.py
echo.
echo To run the daily brief with speech:
echo   uv run python jarvis\daily_brief.py --speak
echo.
echo To start the voice listener:
echo   uv run python jarvis\wake_listener.py
echo.
pause
