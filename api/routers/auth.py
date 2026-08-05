from fastapi import APIRouter, Depends, HTTPException

from api.config import load_api_settings
from api.dependencies import AccessTokenUser, require_user
from api.schemas import CurrentUserResponse, WeChatLoginRequest, WeChatLoginResponse
from api.services.auth import WeChatLoginError, create_access_token, exchange_wechat_code
from api.services.users import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/wechat", response_model=WeChatLoginResponse)
def wechat_login(request: WeChatLoginRequest) -> WeChatLoginResponse:
    settings = load_api_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    try:
        openid = exchange_wechat_code(request.code, settings)
    except (WeChatLoginError, httpx.HTTPError):
        raise HTTPException(status_code=502, detail="WeChat login is unavailable") from None

    user = UserRepository(settings.database_path).get_or_create(openid, set(settings.admin_openids))
    return WeChatLoginResponse(
        access_token=create_access_token(user, settings.jwt_secret),
        user=CurrentUserResponse(id=user.id, role=user.role),
    )


@router.get("/me", response_model=CurrentUserResponse)
def current_user(user: AccessTokenUser = Depends(require_user)) -> CurrentUserResponse:
    return CurrentUserResponse(id=user.id, role=user.role)
