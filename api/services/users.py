"""SQLite-backed users and roles for the first mini-program release."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class User:
    id: str
    openid: str
    role: str


class UserRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    wechat_openid TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'member')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def get_or_create(self, openid: str, admin_openids: set[str]) -> User:
        role = "admin" if openid in admin_openids else "member"
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO users (id, wechat_openid, role) VALUES (?, ?, ?)",
                (uuid4().hex, openid, role),
            )
            if role == "admin":
                connection.execute(
                    "UPDATE users SET role = 'admin' WHERE wechat_openid = ?",
                    (openid,),
                )
            row = connection.execute(
                "SELECT id, wechat_openid, role FROM users WHERE wechat_openid = ?",
                (openid,),
            ).fetchone()

        return User(id=row["id"], openid=row["wechat_openid"], role=row["role"])
