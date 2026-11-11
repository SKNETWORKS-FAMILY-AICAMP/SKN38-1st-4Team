@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -NonInteractive -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8501/_stcore/health' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200 -and $r.Content.Trim() -eq 'ok') { exit 0 } } catch {}; exit 1" >nul 2>&1
if not errorlevel 1 goto running
if /i "%~1"=="--check" exit /b 1
call prepare.bat
if errorlevel 1 goto failed
".venv\Scripts\python.exe" launch.py
if errorlevel 1 goto failed
exit /b 0
:running
echo Streamlit is already running: http://localhost:8501
if /i "%~1"=="--check" exit /b 0
start "" "http://localhost:8501"
exit /b 0
:failed
pause
exit /b 1
