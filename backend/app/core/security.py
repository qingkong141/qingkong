from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


# ── 密码相关 ──────────────────────────────────────

def hash_password(password: str) -> str:
    """明文密码 → bcrypt 哈希"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """验证明文密码是否匹配哈希"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ── Token 相关 ────────────────────────────────────

def create_access_token(user_id: int) -> str:
    """生成短期 access_token（默认 30 分钟）"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    """生成长期 refresh_token（默认 7 天）"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    """解码 Token，返回 payload，失败抛异常"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
