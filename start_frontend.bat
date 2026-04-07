@echo off
setlocal
title Light Inspector Frontend

pushd "%~dp0frontend"
if errorlevel 1 (
  echo [ERROR] Cannot enter frontend directory.
  echo Expected path: "%~dp0frontend"
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm was not found in PATH.
  echo Please install Node.js LTS, then try again.
  pause
  popd
  exit /b 1
)

if not exist "node_modules" (
  echo [1/2] Installing frontend dependencies...
  call npm install
  if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies.
    pause
    popd
    exit /b 1
  )
) else (
  echo [1/2] node_modules already exists. Skipping install.
)

echo [2/2] Starting Vite dev server...
echo Frontend URL: http://127.0.0.1:5173
call npm run dev -- --host 127.0.0.1 --port 5173

popd
pause
