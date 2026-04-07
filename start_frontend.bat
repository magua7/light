@echo off
setlocal EnableExtensions
title Light Inspector Frontend

set "NPM_MIRROR=https://registry.npmmirror.com"

pushd "%~dp0frontend"
if errorlevel 1 (
  echo [ERROR] Cannot enter frontend directory.
  echo Expected path: "%~dp0frontend"
  pause
  exit /b 1
)

echo [1/3] Checking Node.js...

if not exist "package.json" (
  echo [ERROR] package.json was not found in frontend directory.
  pause
  popd
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js was not found in PATH.
  echo [HINT] Please install Node.js LTS and try again.
  pause
  popd
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm was not found in PATH.
  echo [HINT] Please install Node.js LTS and ensure npm is available in PATH.
  pause
  popd
  exit /b 1
)

echo [2/3] Preparing frontend dependencies...
call :install_deps
if errorlevel 1 (
  echo [ERROR] Failed to install frontend dependencies.
  echo [HINT] This is usually a network or npm registry issue, not a project code issue.
  echo [HINT] Manual retry example:
  echo        npm install --registry=%NPM_MIRROR%
  pause
  popd
  exit /b 1
)

echo [3/3] Starting frontend...
echo Frontend URL: http://127.0.0.1:5173
call npm run dev -- --host 127.0.0.1 --port 5173

popd
pause
exit /b 0

:install_deps
if not exist "node_modules" (
  if exist "package-lock.json" (
    echo [INFO] package-lock.json detected. Using npm ci...
    call npm ci
  ) else (
    echo [INFO] package-lock.json not found. Using npm install...
    call npm install
  )

  if not errorlevel 1 exit /b 0

  echo [WARN] Default npm source failed. Retrying once with npmmirror...
  if exist "package-lock.json" (
    call npm ci --registry=%NPM_MIRROR%
  ) else (
    call npm install --registry=%NPM_MIRROR%
  )
  if not errorlevel 1 exit /b 0
  exit /b 1
)

if not exist "node_modules\.bin\vite.cmd" (
  echo [INFO] Existing node_modules is incomplete. Repairing dependencies...
  call npm install
  if not errorlevel 1 exit /b 0

  echo [WARN] Repair install failed. Retrying once with npmmirror...
  call npm install --registry=%NPM_MIRROR%
  if not errorlevel 1 exit /b 0
  exit /b 1
)

echo [INFO] node_modules already exists. Skipping install.
exit /b 0
