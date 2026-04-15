from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
