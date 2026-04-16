import hashlib
import json
import uuid
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.file import File
from app.core.storage import upload_to_minio, upload_stream_to_minio, delete_from_minio
from app.core.redis import redis_client


async def _build_path(parent_id: int | None, db: AsyncSession) -> str:
    if parent_id is None:
        return "/"
    parent = await db.get(File, parent_id)
    if not parent or not parent.is_dir:
        raise ValueError("父文件夹不存在")
    parent_path = parent.path.rstrip("/")
    return f"{parent_path}/{parent.name}"


async def list_files(
    parent_id: int | None,
    owner_id: int,
    db: AsyncSession,
) -> list[File]:
    stmt = (
        select(File)
        .where(
            File.owner_id == owner_id,
            File.is_deleted == False,
            File.parent_id == parent_id,
        )
        .order_by(File.is_dir.desc(), File.name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_folder(
    name: str,
    parent_id: int | None,
    owner_id: int,
    db: AsyncSession,
) -> File:
    path = await _build_path(parent_id, db)

    existing = await db.execute(
        select(File).where(
            File.owner_id == owner_id,
            File.parent_id == parent_id,
            File.name == name,
            File.is_dir == True,
            File.is_deleted == False,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("同名文件夹已存在")

    folder = File(
        name=name,
        path=path,
        parent_id=parent_id,
        size=0,
        is_dir=True,
        owner_id=owner_id,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def rename_file(
    file_id: int,
    new_name: str,
    owner_id: int,
    db: AsyncSession,
) -> File | None:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id:
        return None

    dup = await db.execute(
        select(File).where(
            File.owner_id == owner_id,
            File.parent_id == file.parent_id,
            File.name == new_name,
            File.is_dir == file.is_dir,
            File.is_deleted == False,
            File.id != file_id,
        )
    )
    if dup.scalar_one_or_none():
        raise ValueError("同名文件已存在")

    file.name = new_name
    await db.commit()
    await db.refresh(file)
    return file


async def move_file(
    file_id: int,
    new_parent_id: int | None,
    owner_id: int,
    db: AsyncSession,
) -> File | None:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id:
        return None

    if new_parent_id == file_id:
        raise ValueError("不能移动到自身")

    new_path = await _build_path(new_parent_id, db)

    dup = await db.execute(
        select(File).where(
            File.owner_id == owner_id,
            File.parent_id == new_parent_id,
            File.name == file.name,
            File.is_dir == file.is_dir,
            File.is_deleted == False,
            File.id != file_id,
        )
    )
    if dup.scalar_one_or_none():
        raise ValueError("目标目录下已存在同名文件")

    file.parent_id = new_parent_id
    file.path = new_path
    await db.commit()
    await db.refresh(file)
    return file


async def delete_file(
    file_id: int,
    owner_id: int,
    db: AsyncSession,
) -> bool:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id:
        return False

    file.is_deleted = True

    if file.is_dir:
        await _soft_delete_children(file_id, db)

    await db.commit()
    return True


async def _soft_delete_children(parent_id: int, db: AsyncSession):
    result = await db.execute(
        select(File).where(File.parent_id == parent_id, File.is_deleted == False)
    )
    children = result.scalars().all()
    for child in children:
        child.is_deleted = True
        if child.is_dir:
            await _soft_delete_children(child.id, db)


async def get_file(file_id: int, owner_id: int, db: AsyncSession) -> File | None:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id:
        return None
    return file


async def upload_file(
    filename: str,
    content: bytes,
    content_type: str,
    parent_id: int | None,
    owner_id: int,
    db: AsyncSession,
) -> tuple[File, bool]:
    """
    上传文件，返回 (File, is_instant) 元组。
    is_instant=True 表示秒传（MD5 匹配到已有文件，复用 storage_key）。
    """
    md5 = hashlib.md5(content).hexdigest()
    path = await _build_path(parent_id, db)

    existing = await db.execute(
        select(File).where(
            File.owner_id == owner_id,
            File.md5 == md5,
            File.is_deleted == False,
        )
    )
    existing_file = existing.scalar_one_or_none()

    if existing_file:
        storage_key = existing_file.storage_key
        is_instant = True
    else:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
        storage_key = f"files/{owner_id}/{unique_name}"
        upload_to_minio(storage_key, content, content_type)
        is_instant = False

    file_record = File(
        name=filename,
        path=path,
        parent_id=parent_id,
        size=len(content),
        mime_type=content_type,
        storage_key=storage_key,
        md5=md5,
        owner_id=owner_id,
        is_dir=False,
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    return file_record, is_instant


MULTIPART_KEY_PREFIX = "multipart:"
MULTIPART_EXPIRE = 3600 * 24  # 24 hours


async def init_multipart(
    filename: str,
    total_size: int,
    total_chunks: int,
    parent_id: int | None,
    owner_id: int,
) -> str:
    upload_id = uuid.uuid4().hex
    key = f"{MULTIPART_KEY_PREFIX}{upload_id}"
    meta = {
        "filename": filename,
        "total_size": total_size,
        "total_chunks": total_chunks,
        "parent_id": parent_id,
        "owner_id": owner_id,
        "uploaded_chunks": [],
    }
    await redis_client.set(key, json.dumps(meta), ex=MULTIPART_EXPIRE)
    return upload_id


async def upload_chunk(
    upload_id: str,
    chunk_index: int,
    data: bytes,
    owner_id: int,
) -> dict:
    key = f"{MULTIPART_KEY_PREFIX}{upload_id}"
    raw = await redis_client.get(key)
    if not raw:
        raise ValueError("上传任务不存在或已过期")

    meta = json.loads(raw)
    if meta["owner_id"] != owner_id:
        raise ValueError("无权限")

    temp_key = f"temp/{upload_id}/chunk_{chunk_index:05d}"
    upload_to_minio(temp_key, data, "application/octet-stream")

    uploaded: list = meta["uploaded_chunks"]
    if chunk_index not in uploaded:
        uploaded.append(chunk_index)
        uploaded.sort()
    meta["uploaded_chunks"] = uploaded
    await redis_client.set(key, json.dumps(meta), ex=MULTIPART_EXPIRE)

    return {
        "chunk_index": chunk_index,
        "uploaded": len(uploaded),
        "total": meta["total_chunks"],
    }


async def complete_multipart(
    upload_id: str,
    owner_id: int,
    db: AsyncSession,
) -> tuple[File, bool]:
    key = f"{MULTIPART_KEY_PREFIX}{upload_id}"
    raw = await redis_client.get(key)
    if not raw:
        raise ValueError("上传任务不存在或已过期")

    meta = json.loads(raw)
    if meta["owner_id"] != owner_id:
        raise ValueError("无权限")

    uploaded = meta["uploaded_chunks"]
    total_chunks = meta["total_chunks"]
    if len(uploaded) != total_chunks:
        raise ValueError(f"分片未全部上传，已上传 {len(uploaded)}/{total_chunks}")

    from app.core.storage import get_minio_client
    from app.core.config import settings as app_settings
    client = get_minio_client()

    merged = BytesIO()
    for i in range(total_chunks):
        temp_key = f"temp/{upload_id}/chunk_{i:05d}"
        response = client.get_object(app_settings.MINIO_BUCKET, temp_key)
        merged.write(response.read())
        response.close()
        response.release_conn()

    merged_bytes = merged.getvalue()
    md5 = hashlib.md5(merged_bytes).hexdigest()

    existing = await db.execute(
        select(File).where(
            File.owner_id == owner_id,
            File.md5 == md5,
            File.is_deleted == False,
        )
    )
    existing_file = existing.scalar_one_or_none()

    filename = meta["filename"]
    parent_id = meta["parent_id"]
    path = await _build_path(parent_id, db)

    if existing_file:
        storage_key = existing_file.storage_key
        is_instant = True
    else:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
        storage_key = f"files/{owner_id}/{unique_name}"
        merged.seek(0)
        upload_stream_to_minio(
            storage_key, merged, len(merged_bytes),
            "application/octet-stream",
        )
        is_instant = False

    file_record = File(
        name=filename,
        path=path,
        parent_id=parent_id,
        size=len(merged_bytes),
        mime_type=_guess_mime(filename),
        storage_key=storage_key,
        md5=md5,
        owner_id=owner_id,
        is_dir=False,
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)

    for i in range(total_chunks):
        temp_key = f"temp/{upload_id}/chunk_{i:05d}"
        delete_from_minio(temp_key)

    await redis_client.delete(key)

    return file_record, is_instant


def _guess_mime(filename: str) -> str:
    import mimetypes
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


async def list_trash(owner_id: int, db: AsyncSession) -> list[File]:
    result = await db.execute(
        select(File)
        .where(File.owner_id == owner_id, File.is_deleted == True)
        .order_by(File.updated_at.desc())
    )
    return list(result.scalars().all())


async def restore_file(file_id: int, owner_id: int, db: AsyncSession) -> File | None:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id or not file.is_deleted:
        return None

    file.is_deleted = False

    if file.parent_id:
        parent = await db.get(File, file.parent_id)
        if parent and parent.is_deleted:
            parent.is_deleted = False

    await db.commit()
    await db.refresh(file)
    return file


async def permanent_delete(file_id: int, owner_id: int, db: AsyncSession) -> bool:
    file = await db.get(File, file_id)
    if not file or file.owner_id != owner_id:
        return False

    if not file.is_dir and file.storage_key:
        ref_count = await db.execute(
            select(File).where(
                File.storage_key == file.storage_key,
                File.id != file_id,
            )
        )
        if not ref_count.scalar_one_or_none():
            delete_from_minio(file.storage_key)

    if file.is_dir:
        await _permanent_delete_children(file.id, owner_id, db)

    await db.delete(file)
    await db.commit()
    return True


async def _permanent_delete_children(parent_id: int, owner_id: int, db: AsyncSession):
    result = await db.execute(
        select(File).where(File.parent_id == parent_id)
    )
    children = result.scalars().all()
    for child in children:
        if child.is_dir:
            await _permanent_delete_children(child.id, owner_id, db)
        elif child.storage_key:
            ref_count = await db.execute(
                select(File).where(
                    File.storage_key == child.storage_key,
                    File.id != child.id,
                )
            )
            if not ref_count.scalar_one_or_none():
                delete_from_minio(child.storage_key)
        await db.delete(child)


async def empty_trash(owner_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(File).where(File.owner_id == owner_id, File.is_deleted == True)
    )
    files = result.scalars().all()
    count = 0
    for file in files:
        if not file.is_dir and file.storage_key:
            ref_count = await db.execute(
                select(File).where(
                    File.storage_key == file.storage_key,
                    File.id != file.id,
                    File.is_deleted == False,
                )
            )
            if not ref_count.scalar_one_or_none():
                delete_from_minio(file.storage_key)
        await db.delete(file)
        count += 1
    await db.commit()
    return count


async def get_storage_usage(owner_id: int, db: AsyncSession) -> dict:
    from sqlalchemy import func as sqla_func

    result = await db.execute(
        select(sqla_func.coalesce(sqla_func.sum(File.size), 0))
        .where(File.owner_id == owner_id, File.is_deleted == False, File.is_dir == False)
    )
    used = result.scalar() or 0

    from app.models.user import User
    user = await db.get(User, owner_id)
    quota = user.storage_quota if user else 0

    return {
        "used": used,
        "quota": quota,
        "usedFormatted": _format_size(used),
        "quotaFormatted": _format_size(quota),
        "percentage": round(used / quota * 100, 1) if quota > 0 else 0,
    }


def _format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
