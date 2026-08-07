import asyncio

import httpx
import pytest
from fastapi import HTTPException

from api.dependencies import AccessTokenUser, require_admin
from api.main import create_app


def test_wechat_login_returns_administrator_token_for_configured_openid(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    monkeypatch.setenv("WECHAT_APPID", "test-appid")
    monkeypatch.setenv("WECHAT_APPSECRET", "test-appsecret")
    monkeypatch.setenv("WECHAT_ADMIN_OPENIDS", "admin-openid")

    from api.routers import auth

    monkeypatch.setattr(auth, "exchange_wechat_code", lambda code, settings: "admin-openid")

    async def login() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/api/v1/auth/wechat", json={"code": "wechat-login-code"})

    response = asyncio.run(login())

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
    assert response.json()["access_token"].count(".") == 2


def test_current_user_endpoint_rejects_invalid_token(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")

    async def read_current_user() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer not-a-valid-token"},
            )

    response = asyncio.run(read_current_user())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_administrator_guard_rejects_member_user():
    with pytest.raises(HTTPException) as error:
        require_admin(AccessTokenUser(id="member-id", role="member"))

    assert error.value.status_code == 403
    assert error.value.detail == "Administrator access required"


def test_wechat_login_translates_provider_timeout_to_bad_gateway(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    monkeypatch.setenv("WECHAT_APPID", "test-appid")
    monkeypatch.setenv("WECHAT_APPSECRET", "test-appsecret")

    from api.routers import auth

    def unavailable(*_args, **_kwargs):
        raise httpx.ConnectError("wechat unavailable")

    monkeypatch.setattr(auth, "exchange_wechat_code", unavailable)

    async def login() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/api/v1/auth/wechat", json={"code": "wechat-code"})

    response = asyncio.run(login())

    assert response.status_code == 502
    assert response.json()["detail"] == "WeChat login is unavailable"
