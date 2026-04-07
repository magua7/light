@echo off
setlocal EnableExtensions
title Light Inspector Backend

set "VENV_DIR=.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_CFG=%VENV_DIR%\pyvenv.cfg"
set "VENV_MARKER=%VENV_DIR%\.lightinspector-local"
set "RECREATE_VENV=0"
set "RECREATE_REASON="

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

if exist "%VENV_DIR%" (
  if not exist "%VENV_PYTHON%" (
    set "RECREATE_VENV=1"
    set "RECREATE_REASON=Existing .venv is incomplete."
  ) else if not exist "%VENV_CFG%" (
    set "RECREATE_VENV=1"
    set "RECREATE_REASON=Existing .venv is missing pyvenv.cfg."
  ) else if not exist "%VENV_MARKER%" (
    set "RECREATE_VENV=1"
    set "RECREATE_REASON=Existing .venv was not created by this machine bootstrap script."
  ) else (
    "%VENV_PYTHON%" -c "import sys; print(sys.version)" >nul 2>nul
    if errorlevel 1 (
      set "RECREATE_VENV=1"
      set "RECREATE_REASON=Existing .venv is invalid or was copied from another machine."
    )
  )
)

if "%RECREATE_VENV%"=="1" (
  echo [INFO] %RECREATE_REASON%
  echo [INFO] Removing old virtual environment and recreating it...
  if exist "%VENV_DIR%\*" attrib -r -s -h "%VENV_DIR%\*" /s /d >nul 2>nul
  if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%" >nul 2>nul
  if exist "%VENV_DIR%" (
    echo [ERROR] Failed to remove old .venv.
    echo [ERROR] Please close terminals or tools that may be using backend\.venv, then try again.
    pause
    popd
    exit /b 1
  )
)

if not exist "%VENV_PYTHON%" (
  echo [1/4] Creating virtual environment...
  %PYTHON_CMD% -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    popd
    exit /b 1
  )
)

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

if not exist "%VENV_MARKER%" (
  > "%VENV_MARKER%" echo local-venv-created-by-start_backend
)

echo [4/4] Starting FastAPI server...
echo Backend URL: http://127.0.0.1:8000
echo Health URL : http://127.0.0.1:8000/api/health
"%VENV_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

popd
pause
