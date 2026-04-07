@echo off
setlocal EnableExtensions
title Light Inspector Backend

pushd "%~dp0backend"
if errorlevel 1 (
  echo [ERROR] Cannot enter backend directory.
  echo Expected path: "%~dp0backend"
  pause
  exit /b 1
)

set "PYTHON_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
  echo [ERROR] Python was not found in PATH.
  echo Please install Python 3.10 or newer and enable "Add Python to PATH".
  pause
  popd
  exit /b 1
)

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys; print(sys.version)" >nul 2>nul
  if errorlevel 1 (
    echo [INFO] Existing .venv is invalid or was copied from another machine.
    echo [INFO] Removing old virtual environment and recreating it...
    rmdir /s /q ".venv"
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating virtual environment...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    popd
    exit /b 1
  )
)

set "VENV_PYTHON=.venv\Scripts\python.exe"

echo [2/4] Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip.
  pause
  popd
  exit /b 1
)

echo [3/4] Installing backend dependencies...
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install backend dependencies.
  pause
  popd
  exit /b 1
)

echo [4/4] Starting FastAPI server...
echo Backend URL: http://127.0.0.1:8000
echo Health URL : http://127.0.0.1:8000/api/health
"%VENV_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

popd
pause
