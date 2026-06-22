from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.file import Share
from app.schemas.file import CreateShareRequest, ShareResponse, ShareAccessRequest
from app.services import share as share_service

router = APIRouter(tags=["分享"])



def _share_to_response(share) -> ShareResponse:
    return ShareResponse(
        id=share.id,
        file_id=share.file_id,
        token=share.token,
        has_password=bool(share.password),
        password=share.password,
        expire_at=share.expire_at,
        allow_download=share.allow_download,
        download_count=share.download_count,
        created_at=share.created_at,
        file_name=share.file.name if share.file else "",
        file_size=share.file.size if share.file else 0,
        is_dir=share.file.is_dir if share.file else False,
    )


@router.post("/shares", status_code=201, response_model=ShareResponse)
async def create_share(
    data: CreateShareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        share = await share_service.create_share(
            file_id=data.file_id,
            owner_id=current_user.id,
            password=data.password,
            expire_hours=data.expire_hours,
            allow_download=data.allow_download,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _share_to_response(share)


@router.get("/shares")
async def list_shares(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    shares = await share_service.list_shares(current_user.id, db)
    data = [
        {
            "id": s.id,
            "fileId": s.file_id,
            "token": s.token,
            "hasPassword": bool(s.password),
            "password": s.password,
            "expireAt": s.expire_at.isoformat() if s.expire_at else None,
            "allowDownload": s.allow_download,
            "downloadCount": s.download_count,
            "createdAt": s.created_at.isoformat() if s.created_at else None,
            "fileName": s.file.name if s.file else "",
            "fileSize": s.file.size if s.file else 0,
            "isDir": s.file.is_dir if s.file else False,
        }
        for s in shares
    ]
    return JSONResponse(content=data)


@router.delete("/shares/{share_id}", status_code=204)
async def delete_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await share_service.delete_share(share_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="分享不存在")


@router.post("/s/{token}")
async def access_share(
    token: str,
    data: ShareAccessRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    password = data.password if data else None

    result = await db.execute(select(Share).where(Share.token == token))
    share_record = result.scalar_one_or_none()
    if not share_record:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    if share_record.expire_at and share_record.expire_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="分享链接已过期")

    if share_record.password and not password:
        return {"needPassword": True, "hasPassword": True}

    try:
        share = await share_service.access_share(token, password, db)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return {
        "fileName": share.file.name if share.file else "",
        "fileSize": share.file.size if share.file else 0,
        "isDir": share.file.is_dir if share.file else False,
        "hasPassword": bool(share.password),
        "needPassword": False,
        "allowDownload": share.allow_download,
    }


@router.get("/s/{token}/browse")
async def browse_shared_folder(
    token: str,
    parent_id: int | None = Query(default=None, alias="parentId"),
    password: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """浏览分享的文件夹内容"""
    try:
        share, files = await share_service.browse_shared_folder(token, password, parent_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    items = [
        {
            "id": f.id,
            "name": f.name,
            "size": f.size,
            "mimeType": f.mime_type,
            "isDir": f.is_dir,
            "updatedAt": f.updated_at.isoformat() if f.updated_at else None,
        }
        for f in files
    ]
    return {
        "parentId": parent_id or share.file.id,
        "folderName": share.file.name,
        "allowDownload": share.allow_download,
        "items": items,
    }


@router.post("/s/{token}/download")
async def download_shared(
    token: str,
    data: ShareAccessRequest | None = None,
    file_id: int | None = Query(default=None, alias="fileId"),
    db: AsyncSession = Depends(get_db),
):
    password = data.password if data else None
    try:
        share, url = await share_service.download_shared_file(token, password, db, file_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return {"url": url, "name": share.file.name}


@router.get("/s/{token}/stream")
async def stream_shared(
    token: str,
    password: str | None = None,
    file_id: int | None = Query(default=None, alias="fileId"),
    db: AsyncSession = Depends(get_db),
):
    """后端流代理：视频/音频文件不暴露 MinIO 真实 URL，通过后端转发"""
    from fastapi.responses import Response

    try:
        share, content, mime_type, filename = await share_service.get_share_file_stream(token, password, db, file_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # 用 RFC 5987 编码非 ASCII 文件名
    from urllib.parse import quote
    encoded_filename = quote(filename)
    return Response(
        content=content,
        media_type=mime_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )
