from pydantic import BaseModel, Field


class WeChatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=512)


class CurrentUserResponse(BaseModel):
    id: str
    role: str


class WeChatLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserResponse
