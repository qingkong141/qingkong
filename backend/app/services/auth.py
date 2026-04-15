from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.core.redis import redis_client
from app.core.config import settings


async def register(data: RegisterRequest, db: AsyncSession) -> User:
    """注册新用户"""
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise ValueError("用户名已存在")

    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ValueError("邮箱已被注册")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login(data: LoginRequest, db: AsyncSession) -> dict:
    """登录，返回双 Token，refresh_token 存 Redis"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise ValueError("邮箱或密码错误")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # 存入 Redis，key = refresh_token，value = user_id，过期时间 = 7天
    expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis_client.setex(f"refresh:{refresh_token}", expire_seconds, str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh(refresh_token: str) -> dict:
    """用 refresh_token 换新的 access_token"""
    # 先验证 Token 签名和过期时间
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise ValueError("refresh_token 无效或已过期")

    if payload.get("type") != "refresh":
        raise ValueError("Token 类型错误")

    # 再去 Redis 确认是否存在（注销后 Redis 里会删掉）
    user_id = await redis_client.get(f"refresh:{refresh_token}")
    if not user_id:
        raise ValueError("refresh_token 已失效，请重新登录")

    return {
        "access_token": create_access_token(int(user_id)),
        "token_type": "bearer",
    }


async def logout(refresh_token: str) -> None:
    """注销，删除 Redis 中的 refresh_token"""
    await redis_client.delete(f"refresh:{refresh_token}")
