from __future__ import annotations

import ipaddress
from urllib.parse import urlparse
from pathlib import Path
from uuid import uuid4

import httpx
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


def save_remote_upload(url: str, filename: str, upload_dir: Path) -> Path:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise HTTPException(status_code=422, detail="Cloud storage URL must use HTTPS")
    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise HTTPException(status_code=422, detail="Cloud storage URL is not allowed")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and (address.is_private or address.is_loopback or address.is_link_local):
        raise HTTPException(status_code=422, detail="Cloud storage URL is not allowed")

    name = Path(filename or "").name
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported document type")
    if not name:
        raise HTTPException(status_code=422, detail="Document filename is required")

    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{uuid4().hex}_{name}"
    total = 0
    try:
        with httpx.Client(timeout=30, follow_redirects=False) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > MAX_FILE_BYTES:
                    raise HTTPException(status_code=413, detail="Document exceeds 10 MB")
                with path.open("wb") as output:
                    for chunk in response.iter_bytes(64 * 1024):
                        total += len(chunk)
                        if total > MAX_FILE_BYTES:
                            raise HTTPException(status_code=413, detail="Document exceeds 10 MB")
                        output.write(chunk)
    except HTTPException:
        path.unlink(missing_ok=True)
        raise
    except (httpx.HTTPError, OSError, ValueError):
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail="Cloud storage download failed") from None
    if total == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Document is empty")
    return path
