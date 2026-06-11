@echo off
:: Run as Administrator
:: Sets up daily 7am GSC data pull + revenue intelligence report for SaaSpare

echo Setting up SaaSpare daily GSC pull task...

schtasks /create /tn "SaaSpare Daily GSC Pull" ^
  /tr "cmd /c cd /d C:\Users\smith\intent-engine && uv run python scripts/fetch_gsc.py && uv run python scripts/seo/revenue_intelligence.py >> C:\Users\smith\intent-engine\seo\reports\daily-pull.log 2>&1" ^
  /sc daily /st 07:00 ^
  /ru "%USERNAME%" ^
  /f

if %errorlevel% == 0 (
    echo [OK] SaaSpare Daily GSC Pull scheduled for 7:00 AM daily.
) else (
    echo [FAIL] Could not create task. Try running as Administrator.
)
pause
