from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.file import Share
from app.schemas.file import CreateShareRequest, ShareResponse, ShareAccessRequest
from app.services import share as share_service

router = APIRouter(tags=["分享"])


def _share_to_response(share) -> dict:
    return ShareResponse(
        id=share.id,
        file_id=share.file_id,
        token=share.token,
        has_password=bool(share.password),
        expire_at=share.expire_at,
        download_count=share.download_count,
        created_at=share.created_at,
        file_name=share.file.name if share.file else "",
        file_size=share.file.size if share.file else 0,
        is_dir=share.file.is_dir if share.file else False,
    ).model_dump(by_alias=True)


@router.post("/shares", status_code=201)
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
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _share_to_response(share)


@router.get("/shares", response_model=list[ShareResponse])
async def list_shares(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    shares = await share_service.list_shares(current_user.id, db)
    return [_share_to_response(s) for s in shares]


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
    }


@router.post("/s/{token}/download")
async def download_shared(
    token: str,
    data: ShareAccessRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    password = data.password if data else None
    try:
        share, url = await share_service.download_shared_file(token, password, db)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return {"url": url, "name": share.file.name}
