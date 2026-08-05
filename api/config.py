"""Configuration shared by the HTTP API modules."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ApiSettings:
    upload_dir: Path
    database_path: Path
    cors_origins: tuple[str, ...]
    jwt_secret: str
    wechat_appid: str
    wechat_appsecret: str
    admin_openids: frozenset[str]


def load_api_settings() -> ApiSettings:
    upload_dir = Path(os.getenv("API_UPLOAD_DIR", PROJECT_DIR / "uploaded_docs"))
    database_path = Path(os.getenv("API_DATABASE_PATH", PROJECT_DIR / "api.sqlite3"))
    origins = os.getenv("API_CORS_ORIGINS", "http://localhost,https://servicewechat.com")
    admin_openids = frozenset(
        openid.strip() for openid in os.getenv("WECHAT_ADMIN_OPENIDS", "").split(",") if openid.strip()
    )
    return ApiSettings(
        upload_dir=upload_dir,
        database_path=database_path,
        cors_origins=tuple(origin.strip() for origin in origins.split(",") if origin.strip()),
        jwt_secret=os.getenv("API_JWT_SECRET", ""),
        wechat_appid=os.getenv("WECHAT_APPID", ""),
        wechat_appsecret=os.getenv("WECHAT_APPSECRET", ""),
        admin_openids=admin_openids,
    )
