"""WeChat code exchange and access-token helpers."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import jwt

from api.config import ApiSettings
from api.services.users import User


class WeChatLoginError(RuntimeError):
    """Raised when WeChat does not return a usable OpenID."""


def exchange_wechat_code(code: str, settings: ApiSettings) -> str:
    if not (settings.wechat_appid and settings.wechat_appsecret):
        raise WeChatLoginError("WeChat credentials are not configured")

    response = httpx.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={
            "appid": settings.wechat_appid,
            "secret": settings.wechat_appsecret,
            "js_code": code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    openid = payload.get("openid")
    if not openid:
        raise WeChatLoginError("WeChat did not return an OpenID")
    return openid


def create_access_token(user: User, secret: str) -> str:
    issued_at = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": user.id,
            "role": user.role,
            "iat": issued_at,
            "exp": issued_at + timedelta(days=7),
        },
        secret,
        algorithm="HS256",
    )
