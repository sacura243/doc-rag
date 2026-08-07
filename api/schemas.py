from pydantic import BaseModel, Field


class WeChatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=512)


class ImportDocumentRequest(BaseModel):
    url: str = Field(min_length=1, max_length=4096)
    filename: str = Field(min_length=1, max_length=255)


class CurrentUserResponse(BaseModel):
    id: str
    role: str
    openid: str | None = None


class WeChatLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserResponse
