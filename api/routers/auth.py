from fastapi import APIRouter, Depends, HTTPException
import httpx
import logging
import os

from api.config import load_api_settings
from api.dependencies import AccessTokenUser, require_user
from api.schemas import CurrentUserResponse, WeChatLoginRequest, WeChatLoginResponse
from api.services.auth import WeChatLoginError, create_access_token, exchange_wechat_code
from api.services.users import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/wechat", response_model=WeChatLoginResponse)
def wechat_login(request: WeChatLoginRequest) -> WeChatLoginResponse:
    settings = load_api_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    try:
        openid = exchange_wechat_code(request.code, settings)
    except WeChatLoginError as error:
        logger.warning("WeChat login rejected: %s", error)
        raise HTTPException(status_code=502, detail="WeChat login is unavailable") from None
    except httpx.HTTPError as error:
        logger.warning("WeChat login HTTP error type=%s", type(error).__name__)
        raise HTTPException(status_code=502, detail="WeChat login is unavailable") from None

    user = UserRepository(settings.database_path).get_or_create(openid, set(settings.admin_openids))
    return WeChatLoginResponse(
        access_token=create_access_token(user, settings.jwt_secret),
        user=CurrentUserResponse(id=user.id, role=user.role),
    )


@router.post("/development", response_model=WeChatLoginResponse)
def development_login() -> WeChatLoginResponse:
    if os.getenv("API_ENV", "development") != "development":
        raise HTTPException(status_code=404, detail="Not found")
    settings = load_api_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    openid = os.getenv("WECHAT_DEV_OPENID", "local-admin")
    user = UserRepository(settings.database_path).get_or_create(openid, {openid})
    return WeChatLoginResponse(access_token=create_access_token(user, settings.jwt_secret), user=CurrentUserResponse(id=user.id, role=user.role))


@router.get("/me", response_model=CurrentUserResponse)
def current_user(user: AccessTokenUser = Depends(require_user)) -> CurrentUserResponse:
    return CurrentUserResponse(id=user.id, role=user.role)
