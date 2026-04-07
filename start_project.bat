@echo off
setlocal EnableExtensions
title Light Inspector Launcher

if not exist "%~dp0start_backend.bat" (
  echo [ERROR] start_backend.bat was not found.
  pause
  exit /b 1
)

if not exist "%~dp0start_frontend.bat" (
  echo [ERROR] start_frontend.bat was not found.
  pause
  exit /b 1
)

echo Starting LightInspector...

start "Light Inspector Backend" "%ComSpec%" /k call "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "Light Inspector Frontend" "%ComSpec%" /k call "%~dp0start_frontend.bat"
timeout /t 6 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo Browser launch requested.
echo If frontend dependencies are still installing, wait a moment and refresh the page.
exit /b 0
