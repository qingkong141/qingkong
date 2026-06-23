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
    allow_download: bool = True,
    db: AsyncSession = None,
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
        allow_download=allow_download,
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
    """返回下载链接（仅 allow_download=True 时调用）"""
    share = await access_share(token, password, db)

    if not share.file or not share.file.storage_key:
        raise ValueError("文件不存在")
    if not share.allow_download:
        raise ValueError("此分享不允许下载，请使用在线播放")

    share.download_count += 1
    await db.commit()

    from app.core.storage import get_presigned_url
    url = get_presigned_url(share.file.storage_key, filename=share.file.name)
    return share, url


async def get_share_file_stream(
    token: str,
    password: str | None,
    db: AsyncSession,
    file_id: int | None = None,
) -> tuple[Share, bytes, str, str]:
    """获取分享文件的原始数据（后端流代理用），返回 (share, data, mime_type, filename)"""
    share = await access_share(token, password, db)
    target = await _resolve_shared_file(share, file_id, db)

    from app.core.storage import get_minio_client
    from app.core.config import settings

    client = get_minio_client()
    try:
        response = client.get_object(settings.MINIO_BUCKET, target.storage_key)
        data = response.read()
    finally:
        response.close()
        response.release_conn()

    share.download_count += 1
    await db.commit()

    return share, data, target.mime_type or "application/octet-stream", target.name


async def browse_shared_folder(
    token: str,
    password: str | None,
    parent_id: int | None,
    db: AsyncSession,
) -> tuple[Share, list[File]]:
    """浏览分享的文件夹内容"""
    share = await access_share(token, password, db)

    if not share.file.is_dir:
        raise ValueError("此分享不是文件夹，不支持浏览")

    # 没传 parentId 就从分享的文件夹根开始
    if parent_id is None:
        parent_id = share.file.id

    # 验证 parent_id 是目录且属于同一用户
    parent = await db.get(File, parent_id)
    if not parent or not parent.is_dir:
        raise ValueError("目录不存在")
    if parent.owner_id != share.owner_id:
        raise ValueError("无权访问")

    stmt = (
        select(File)
        .where(
            File.parent_id == parent_id,
            File.is_deleted == False,
        )
        .order_by(File.is_dir.desc(), File.name)
    )
    result = await db.execute(stmt)
    return share, list(result.scalars().all())


async def _resolve_shared_file(share: Share, file_id: int | None, db: AsyncSession) -> File:
    """解析要操作的共享文件：file_id 为空则取分享文件本身，否则从分享文件夹中找"""
    if file_id is None:
        if not share.file or not share.file.storage_key:
            raise ValueError("文件不存在")
        return share.file

    # 子文件：必须是分享文件夹的子文件
    if not share.file.is_dir:
        raise ValueError("此分享是单文件，不支持子文件操作")
    child = await db.get(File, file_id)
    if not child or child.is_dir or not child.storage_key:
        raise ValueError("文件不存在或不是有效文件")
    if child.owner_id != share.owner_id:
        raise ValueError("无权访问")
    return child


async def download_shared_file(
    token: str,
    password: str | None,
    db: AsyncSession,
    file_id: int | None = None,
) -> tuple[Share, str]:
    """返回下载链接（仅 allow_download=True 时调用）。
    返回后端代理 URL，浏览器不直接访问 MinIO。
    file_id 为空则下载分享文件本身，否则下载分享文件夹内的子文件。
    """
    share = await access_share(token, password, db)

    if not share.allow_download:
        raise ValueError("此分享不允许下载，请使用在线播放")

    target = await _resolve_shared_file(share, file_id, db)

    share.download_count += 1
    await db.commit()

    # 走后端代理，不暴露 MinIO 地址
    from urllib.parse import quote
    fid = f"&fileId={file_id}" if file_id else ""
    pw = f"&password={quote(password or '')}" if password else ""
    url = f"/yunpan/s/{token}/dl?{fid}{pw}".replace("?&", "?")
    return share, url
