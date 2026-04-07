@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Light Inspector Backend

set "PRIMARY_VENV=.venv"
set "FALLBACK_VENV=.venv_bootstrap"
set "PREPARED_VENV="
set "PYTHON_CMD="
set "TSINGHUA_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple"
set "TSINGHUA_HOST=pypi.tuna.tsinghua.edu.cn"
set "PIP_DEFAULT_TIMEOUT=30"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

pushd "%~dp0backend"
if errorlevel 1 (
  echo [ERROR] Cannot enter backend directory.
  echo Expected path: "%~dp0backend"
  pause
  exit /b 1
)

echo [1/4] Checking Python...
call :find_python
if errorlevel 1 (
  echo [ERROR] Python was not found in PATH.
  echo [HINT] Please install Python 3.10 or newer and enable "Add Python to PATH".
  pause
  popd
  exit /b 1
)

echo [2/4] Preparing virtual environment...
call :prepare_venv "%PRIMARY_VENV%"
if errorlevel 1 (
  echo [WARN] Primary virtual environment "%PRIMARY_VENV%" is unavailable.
  echo [WARN] Trying fallback environment "%FALLBACK_VENV%"...
  call :prepare_venv "%FALLBACK_VENV%"
  if errorlevel 1 (
    echo [ERROR] Failed to prepare any usable virtual environment.
    echo [HINT] This usually means backend\.venv is locked by another terminal, editor, or Python process.
    echo [HINT] Please close related tools and try again.
    pause
    popd
    exit /b 1
  )
)

set "ACTIVE_VENV=%PREPARED_VENV%"
set "ACTIVE_PYTHON=%ACTIVE_VENV%\Scripts\python.exe"
set "ACTIVE_MARKER=%ACTIVE_VENV%\.lightinspector-local"

echo [3/4] Installing backend dependencies...
call :show_proxy_info

echo [INFO] Upgrading pip...
call :pip_with_retry "%ACTIVE_PYTHON%" install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip.
  call :print_pip_help
  pause
  popd
  exit /b 1
)

echo [INFO] Installing requirements from requirements.txt...
call :pip_with_retry "%ACTIVE_PYTHON%" install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install backend dependencies.
  call :print_pip_help
  pause
  popd
  exit /b 1
)

if not exist "%ACTIVE_MARKER%" (
  > "%ACTIVE_MARKER%" echo local-venv-created-by-start_backend
)

echo [4/4] Starting backend...
echo Backend URL: http://127.0.0.1:8000
echo Health URL : http://127.0.0.1:8000/api/health
"%ACTIVE_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

popd
pause
exit /b 0

:find_python
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD exit /b 1

for /f "usebackq delims=" %%I in (`%PYTHON_CMD% --version 2^>^&1`) do set "PYTHON_VERSION=%%I"
if defined PYTHON_VERSION echo [INFO] !PYTHON_VERSION!
echo [INFO] Using launcher: !PYTHON_CMD!
exit /b 0

:prepare_venv
set "TARGET_VENV=%~1"
set "TARGET_PYTHON=%TARGET_VENV%\Scripts\python.exe"
set "TARGET_CFG=%TARGET_VENV%\pyvenv.cfg"
set "TARGET_MARKER=%TARGET_VENV%\.lightinspector-local"
set "RECREATE_TARGET=0"
set "RECREATE_REASON="

if exist "%TARGET_VENV%" (
  if not exist "%TARGET_PYTHON%" (
    set "RECREATE_TARGET=1"
    set "RECREATE_REASON=Existing %TARGET_VENV% is incomplete."
  ) else if not exist "%TARGET_CFG%" (
    set "RECREATE_TARGET=1"
    set "RECREATE_REASON=Existing %TARGET_VENV% is missing pyvenv.cfg."
  ) else if not exist "%TARGET_MARKER%" (
    set "RECREATE_TARGET=1"
    set "RECREATE_REASON=Existing %TARGET_VENV% was not created by this bootstrap script."
  ) else (
    "%TARGET_PYTHON%" -c "import sys" >nul 2>nul
    if errorlevel 1 (
      set "RECREATE_TARGET=1"
      set "RECREATE_REASON=Existing %TARGET_VENV% is invalid or copied from another machine."
    )
  )
)

if "!RECREATE_TARGET!"=="1" (
  echo [INFO] !RECREATE_REASON!
  call :remove_directory "%TARGET_VENV%"
  if errorlevel 1 exit /b 1
)

if not exist "%TARGET_PYTHON%" (
  echo [INFO] Creating virtual environment at %TARGET_VENV%...
  %PYTHON_CMD% -m venv "%TARGET_VENV%"
  if errorlevel 1 (
    echo [ERROR] Failed to create %TARGET_VENV%.
    exit /b 1
  )
)

set "PREPARED_VENV=%TARGET_VENV%"
exit /b 0

:remove_directory
set "TARGET_DIR=%~1"
if not exist "%TARGET_DIR%" exit /b 0

echo [INFO] Removing "%TARGET_DIR%"...
if exist "%TARGET_DIR%\*" attrib -r -s -h "%TARGET_DIR%\*" /s /d >nul 2>nul
rmdir /s /q "%TARGET_DIR%" >nul 2>nul

if exist "%TARGET_DIR%" (
  echo [WARN] "%TARGET_DIR%" is locked or still in use.
  exit /b 1
)

exit /b 0

:show_proxy_info
set "HAS_PROXY_INFO=0"
if defined HTTP_PROXY (
  echo [INFO] HTTP_PROXY is set.
  set "HAS_PROXY_INFO=1"
)
if defined HTTPS_PROXY (
  echo [INFO] HTTPS_PROXY is set.
  set "HAS_PROXY_INFO=1"
)
if defined ALL_PROXY (
  echo [INFO] ALL_PROXY is set.
  set "HAS_PROXY_INFO=1"
)
if defined PIP_INDEX_URL (
  echo [INFO] PIP_INDEX_URL is set.
  set "HAS_PROXY_INFO=1"
)
if "!HAS_PROXY_INFO!"=="0" (
  echo [INFO] No proxy-related environment variables detected.
)
exit /b 0

:pip_with_retry
setlocal EnableDelayedExpansion
set "TARGET_PYTHON=%~1"
shift
set "PIP_ARGS=%*"
set "RESULT=1"

"%TARGET_PYTHON%" -m pip !PIP_ARGS!
if not errorlevel 1 (
  set "RESULT=0"
  goto :pip_done
)

echo [WARN] Default pip source failed. Retrying once with Tsinghua mirror...
"%TARGET_PYTHON%" -m pip !PIP_ARGS! -i %TSINGHUA_INDEX% --trusted-host %TSINGHUA_HOST%
if not errorlevel 1 (
  set "RESULT=0"
  goto :pip_done
)

set "HAS_PROXY=0"
if defined HTTP_PROXY set "HAS_PROXY=1"
if defined HTTPS_PROXY set "HAS_PROXY=1"
if defined ALL_PROXY set "HAS_PROXY=1"
if defined http_proxy set "HAS_PROXY=1"
if defined https_proxy set "HAS_PROXY=1"
if defined all_proxy set "HAS_PROXY=1"

if "!HAS_PROXY!"=="1" (
  echo [WARN] Proxy variables were detected. Retrying once without proxy variables...
  set "OLD_HTTP_PROXY=!HTTP_PROXY!"
  set "OLD_HTTPS_PROXY=!HTTPS_PROXY!"
  set "OLD_ALL_PROXY=!ALL_PROXY!"
  set "OLD_http_proxy=!http_proxy!"
  set "OLD_https_proxy=!https_proxy!"
  set "OLD_all_proxy=!all_proxy!"

  set "HTTP_PROXY="
  set "HTTPS_PROXY="
  set "ALL_PROXY="
  set "http_proxy="
  set "https_proxy="
  set "all_proxy="

  "%TARGET_PYTHON%" -m pip !PIP_ARGS! -i %TSINGHUA_INDEX% --trusted-host %TSINGHUA_HOST%
  if not errorlevel 1 (
    set "RESULT=0"
  )
)

:pip_done
endlocal & exit /b %RESULT%

:print_pip_help
echo [HINT] This usually does NOT mean the package version does not exist.
echo [HINT] For example, "fastapi==0.115.6" exists. A failure here is usually caused by:
echo [HINT] 1. Network access to PyPI failed
echo [HINT] 2. HTTP_PROXY / HTTPS_PROXY points to an unavailable proxy
echo [HINT] 3. PIP_INDEX_URL is set to an unreachable index
echo [HINT] The script has already retried with the Tsinghua mirror once.
echo [HINT] Manual retry example:
echo        "%ACTIVE_PYTHON%" -m pip install -r requirements.txt -i %TSINGHUA_INDEX% --trusted-host %TSINGHUA_HOST%
exit /b 0
