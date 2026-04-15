from pydantic import EmailStr
from app.schemas.base import BaseSchema


class RegisterRequest(BaseSchema):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseSchema):
    email: EmailStr
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
