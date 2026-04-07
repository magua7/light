@echo off
setlocal
title Light Inspector Backend

pushd "%~dp0backend"
if errorlevel 1 (
  echo [ERROR] Cannot enter backend directory.
  echo Expected path: "%~dp0backend"
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python was not found in PATH.
  echo Please install Python 3.10 or newer, then try again.
  pause
  popd
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    popd
    exit /b 1
  )
)

echo [2/4] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip.
  pause
  popd
  exit /b 1
)

echo [3/4] Installing backend dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install backend dependencies.
  pause
  popd
  exit /b 1
)

echo [4/4] Starting FastAPI server...
echo Backend URL: http://127.0.0.1:8000
echo Health URL : http://127.0.0.1:8000/api/health
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

popd
pause
