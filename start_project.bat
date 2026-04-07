@echo off
setlocal
title Light Inspector Launcher

echo Starting Light Inspector...

start "Light Inspector Backend" cmd /k call "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "Light Inspector Frontend" cmd /k call "%~dp0start_frontend.bat"
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo Browser launch requested.
echo If frontend dependencies are still installing, wait a moment and refresh the page.
exit /b 0
