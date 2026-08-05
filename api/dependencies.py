from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.config import load_api_settings


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AccessTokenUser:
    id: str
    role: str


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AccessTokenUser:
    settings = load_api_settings()
    if not credentials or not settings.jwt_secret:
        raise HTTPException(status_code=401, detail="Invalid access token")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id = payload["sub"]
        role = payload["role"]
    except (jwt.InvalidTokenError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid access token") from None
    if role not in {"admin", "member"}:
        raise HTTPException(status_code=401, detail="Invalid access token")
    return AccessTokenUser(id=user_id, role=role)


def require_admin(user: AccessTokenUser = Depends(require_user)) -> AccessTokenUser:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
