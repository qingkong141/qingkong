import secrets
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.file import File, Share


def _generate_token(length: int = 12) -> str:
    return secrets.token_urlsafe(length)[:length]


async def create_share(
    file_id: int,
    owner_id: int,
    password: str | None,
    expire_hours: int | None,
    db: AsyncSession,
) -> Share:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id:
        raise ValueError("文件不存在")

    token = _generate_token()
    while await db.execute(select(Share).where(Share.token == token)):
        result = await db.execute(select(Share).where(Share.token == token))
        if result.scalar_one_or_none() is None:
            break
        token = _generate_token()

    expire_at = None
    if expire_hours:
        expire_at = datetime.utcnow() + timedelta(hours=expire_hours)

    share = Share(
        file_id=file_id,
        owner_id=owner_id,
        token=token,
        password=password,
        expire_at=expire_at,
    )
    db.add(share)
    await db.commit()
    await db.refresh(share, attribute_names=["file"])
    return share


async def list_shares(owner_id: int, db: AsyncSession) -> list[Share]:
    result = await db.execute(
        select(Share)
        .where(Share.owner_id == owner_id)
        .options(selectinload(Share.file))
        .order_by(Share.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_share(share_id: int, owner_id: int, db: AsyncSession) -> bool:
    share = await db.get(Share, share_id)
    if not share or share.owner_id != owner_id:
        return False
    await db.delete(share)
    await db.commit()
    return True


async def access_share(
    token: str,
    password: str | None,
    db: AsyncSession,
) -> Share:
    result = await db.execute(
        select(Share)
        .where(Share.token == token)
        .options(selectinload(Share.file))
    )
    share = result.scalar_one_or_none()
    if not share:
        raise ValueError("分享链接不存在")

    if share.expire_at and share.expire_at < datetime.utcnow():
        raise ValueError("分享链接已过期")

    if share.password:
        if not password or password != share.password:
            raise ValueError("密码错误")

    return share


async def download_shared_file(
    token: str,
    password: str | None,
    db: AsyncSession,
) -> tuple[Share, str]:
    share = await access_share(token, password, db)

    if not share.file or not share.file.storage_key:
        raise ValueError("文件不存在")

    share.download_count += 1
    await db.commit()

    from app.core.storage import get_presigned_url
    url = get_presigned_url(share.file.storage_key)
    return share, url
