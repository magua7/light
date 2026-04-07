import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def save_upload_file(upload_file: UploadFile, task_no: str, direction: str) -> dict:
    suffix = Path(upload_file.filename or "").suffix or ".jpg"
    relative_dir = Path(task_no)
    absolute_dir = settings.upload_dir / relative_dir
    absolute_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{direction}_{uuid4().hex[:8]}{suffix.lower()}"
    absolute_path = absolute_dir / filename

    with absolute_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    relative_path = relative_dir / filename
    return {
        "file_path": relative_path.as_posix(),
        "original_name": upload_file.filename or filename,
    }


def build_file_url(relative_path: str) -> str:
    return f"/uploads/{relative_path}"
