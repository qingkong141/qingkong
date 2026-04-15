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
    """
    用 refresh_token 换新的 access_token，同时轮换 refresh_token。
    轮换策略：旧 token 立即从 Redis 删除，颁发全新的 refresh_token。
    效果：每个 refresh_token 只能用一次，第二次调用必然失败，从根源断掉循环。
    """
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise ValueError("refresh_token 无效或已过期")

    if payload.get("type") != "refresh":
        raise ValueError("Token 类型错误")

    user_id = await redis_client.get(f"refresh:{refresh_token}")
    if not user_id:
        raise ValueError("refresh_token 已失效，请重新登录")

    # 旧 token 立即作废
    await redis_client.delete(f"refresh:{refresh_token}")

    # 颁发新的双 token
    new_access = create_access_token(int(user_id))
    new_refresh = create_refresh_token(int(user_id))

    expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis_client.setex(f"refresh:{new_refresh}", expire_seconds, str(user_id))

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


async def logout(refresh_token: str) -> None:
    """注销，删除 Redis 中的 refresh_token"""
    await redis_client.delete(f"refresh:{refresh_token}")


async def change_password(
    user: User,
    old_password: str,
    new_password: str,
    db: AsyncSession,
) -> None:
    """修改密码"""
    if not verify_password(old_password, user.password_hash):
        raise ValueError("原密码错误")

    user.password_hash = hash_password(new_password)
    await db.commit()


async def update_avatar(user: User, avatar_url: str, db: AsyncSession) -> User:
    """更新头像 URL"""
    user.avatar = avatar_url
    await db.commit()
    await db.refresh(user)
    return user
