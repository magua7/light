from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent
PRIMARY_VENV = BACKEND_DIR / ".venv"
FALLBACK_VENV = BACKEND_DIR / ".venv_bootstrap"
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"
TSINGHUA_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
TSINGHUA_HOST = "pypi.tuna.tsinghua.edu.cn"
MIN_PYTHON = (3, 10)


def step(index: int, total: int, message: str) -> None:
    print(f"[{index}/{total}] {message}")


def info(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def error(message: str) -> None:
    print(f"[ERROR] {message}")


def hint(message: str) -> None:
    print(f"[HINT] {message}")


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_cfg(venv_dir: Path) -> Path:
    return venv_dir / "pyvenv.cfg"


def _on_rm_error(func, path, exc_info) -> None:  # noqa: ANN001
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def run_command(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        text=True,
        capture_output=capture_output,
    )


def remove_directory(target: Path) -> bool:
    if not target.exists():
        return True
    try:
        shutil.rmtree(target, onerror=_on_rm_error)
        return not target.exists()
    except Exception as exc:
        warn(f'Failed to remove "{target.name}": {exc}')
        return False


def inspect_venv(venv_dir: Path) -> tuple[bool, str]:
    if not venv_dir.exists():
        return False, f'"{venv_dir.name}" does not exist.'

    active_python = venv_python(venv_dir)
    if not active_python.exists():
        return False, f'"{venv_dir.name}" is missing {active_python.relative_to(venv_dir)}.'

    config_file = venv_cfg(venv_dir)
    if not config_file.exists():
        return False, f'"{venv_dir.name}" is missing pyvenv.cfg.'

    probe = run_command(
        [str(active_python), "-c", "import sys; print(sys.executable)"],
        capture_output=True,
    )
    if probe.returncode != 0:
        stderr = (probe.stderr or "").strip()
        suffix = f" Details: {stderr}" if stderr else ""
        return False, f'"{venv_dir.name}" exists but its Python cannot start.{suffix}'

    return True, f'"{venv_dir.name}" is valid.'


def create_venv(venv_dir: Path) -> bool:
    info(f'Creating virtual environment at "{venv_dir.name}"...')
    result = run_command([sys.executable, "-m", "venv", str(venv_dir)])
    if result.returncode != 0:
        error(f'Failed to create virtual environment "{venv_dir.name}".')
        hint("Please verify that your system Python includes the venv module.")
        return False
    return True


def ensure_clean_venv(venv_dir: Path) -> Path | None:
    is_valid, reason = inspect_venv(venv_dir)
    if is_valid:
        info(reason)
        return venv_dir

    if not venv_dir.exists():
        if create_venv(venv_dir):
            return venv_dir
        return None

    warn(reason)
    if not remove_directory(venv_dir):
        return None

    info(f'Removed invalid "{venv_dir.name}". Recreating it...')
    if create_venv(venv_dir):
        return venv_dir
    return None


def prepare_virtual_environment() -> Path | None:
    primary_valid, primary_reason = inspect_venv(PRIMARY_VENV)
    if primary_valid:
        info(primary_reason)
        return PRIMARY_VENV

    if PRIMARY_VENV.exists():
        warn(primary_reason)
        if remove_directory(PRIMARY_VENV):
            info("Removed invalid .venv successfully. Recreating it...")
            if create_venv(PRIMARY_VENV):
                return PRIMARY_VENV
            return None

        warn(".venv is locked or still in use. Falling back to .venv_bootstrap.")
        hint("Close terminals, editors, or Python processes using backend\\.venv if you want to recover it later.")
        fallback = ensure_clean_venv(FALLBACK_VENV)
        if fallback is None:
            error('Failed to prepare fallback environment ".venv_bootstrap".')
            hint("Please close tools using backend\\.venv_bootstrap, then run the script again.")
        return fallback

    created_primary = ensure_clean_venv(PRIMARY_VENV)
    if created_primary is not None:
        return created_primary

    warn('Failed to prepare ".venv". Trying ".venv_bootstrap"...')
    fallback = ensure_clean_venv(FALLBACK_VENV)
    if fallback is None:
        error("Could not prepare any usable virtual environment.")
    return fallback


def has_proxy_related_env() -> bool:
    keys = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
    ]
    found = False
    for key in keys:
        if os.environ.get(key):
            info(f"{key} is set.")
            found = True
    if not found:
        info("No proxy-related environment variables detected.")
    return found


def pip_run(venv_py: Path, args: list[str], *, env_overrides: dict[str, str] | None = None) -> int:
    effective_env = os.environ.copy()
    effective_env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    effective_env.setdefault("PIP_DEFAULT_TIMEOUT", "30")
    if env_overrides:
        effective_env.update(env_overrides)

    result = run_command([str(venv_py), "-m", "pip", *args], env=effective_env)
    return result.returncode


def print_pip_failure_help(venv_py: Path) -> None:
    error("Pip installation failed.")
    hint("This usually does NOT mean the package version does not exist.")
    hint("For example, fastapi==0.115.6 exists.")
    hint("The more likely cause is a network, proxy, or package index problem.")
    hint(
        f'Manual retry example: "{venv_py}" -m pip install -r requirements.txt -i {TSINGHUA_INDEX} --trusted-host {TSINGHUA_HOST}'
    )


def pip_with_retry(venv_py: Path, args: list[str]) -> bool:
    if pip_run(venv_py, args) == 0:
        return True

    warn("Default pip source failed. Retrying once with Tsinghua mirror...")
    mirror_args = [*args, "-i", TSINGHUA_INDEX, "--trusted-host", TSINGHUA_HOST]
    if pip_run(venv_py, mirror_args) == 0:
        return True

    if has_proxy_related_env():
        warn("Proxy variables were detected. Retrying once without proxy variables...")
        clean_env = {
            "HTTP_PROXY": "",
            "HTTPS_PROXY": "",
            "ALL_PROXY": "",
            "http_proxy": "",
            "https_proxy": "",
            "all_proxy": "",
            "PIP_INDEX_URL": "",
            "PIP_EXTRA_INDEX_URL": "",
        }
        if pip_run(venv_py, mirror_args, env_overrides=clean_env) == 0:
            return True

    print_pip_failure_help(venv_py)
    return False


def main() -> int:
    total_steps = 5

    step(1, total_steps, "Checking Python version...")
    if sys.version_info < MIN_PYTHON:
        error("Python 3.10 or newer is required.")
        hint(f"Current version: {sys.version.split()[0]}")
        return 1
    info(f"Detected Python {sys.version.split()[0]}")

    step(2, total_steps, "Preparing virtual environment...")
    active_venv = prepare_virtual_environment()
    if active_venv is None:
        return 1

    active_python = venv_python(active_venv)
    valid, reason = inspect_venv(active_venv)
    if not valid:
        error(reason)
        return 1
    info(f'Using virtual environment: "{active_venv.name}"')

    step(3, total_steps, "Upgrading pip...")
    if not pip_with_retry(active_python, ["install", "--upgrade", "pip"]):
        return 1

    step(4, total_steps, "Installing dependencies...")
    if not REQUIREMENTS_FILE.exists():
        error("requirements.txt was not found.")
        hint(f'Expected path: "{REQUIREMENTS_FILE}"')
        return 1
    if not pip_with_retry(active_python, ["install", "-r", str(REQUIREMENTS_FILE)]):
        return 1

    step(5, total_steps, "Starting backend...")
    info("Backend URL: http://127.0.0.1:8000")
    info("Health URL : http://127.0.0.1:8000/api/health")
    result = run_command(
        [
            str(active_python),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ]
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
