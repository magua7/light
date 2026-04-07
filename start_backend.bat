@echo off
setlocal EnableExtensions
title Light Inspector Backend

set "PYTHON_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
  echo [ERROR] Python was not found in PATH.
  echo [HINT] Please install Python 3.10 or newer and enable "Add Python to PATH".
  pause
  exit /b 1
)

pushd "%~dp0backend"
if errorlevel 1 (
  echo [ERROR] Cannot enter backend directory.
  echo Expected path: "%~dp0backend"
  pause
  exit /b 1
)

%PYTHON_CMD% scripts\bootstrap_backend.py
set "EXIT_CODE=%ERRORLEVEL%"

popd
pause
exit /b %EXIT_CODE%
