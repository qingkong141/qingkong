from app.schemas.base import BaseSchema


class RegisterRequest(BaseSchema):
    username: str
    email: str
    password: str


class LoginRequest(BaseSchema):
    account: str   # 用户名或邮箱均可
    password: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserMeResponse(BaseSchema):
    id: int
    username: str
    email: str
    avatar: str | None
    is_admin: bool = False
    storage_used: int = 0
    storage_quota: int = 0
