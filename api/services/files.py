from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_FILE_BYTES = 10 * 1024 * 1024


async def save_upload(upload: UploadFile, upload_dir: Path) -> Path:
    name = Path(upload.filename or "").name
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported document type")
    content = await upload.read()
    if not content:
        raise HTTPException(status_code=422, detail="Document is empty")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="Document exceeds 10 MB")
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{uuid4().hex}_{name}"
    path.write_bytes(content)
    return path
