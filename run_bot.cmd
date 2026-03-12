@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found at .venv
  exit /b 1
)

set "MODE=%~1"

if /I "%MODE%"=="--once" (
  powershell -ExecutionPolicy Bypass -File "scripts\dev_runner.ps1" -Watch:$false
  exit /b %ERRORLEVEL%
)

echo Starting in watch mode. Use run_bot.cmd --once for a single run.
powershell -ExecutionPolicy Bypass -File "scripts\dev_runner.ps1"
