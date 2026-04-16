from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.tag import CreateTagRequest, UpdateTagRequest, TagResponse
from app.services import tag as tag_service

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await tag_service.list_tags(db)


@router.get("/slug/{slug}", response_model=TagResponse)
async def get_tag_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    tag = await tag_service.get_by_slug(slug, db)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: CreateTagRequest,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await tag_service.create_tag(data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    data: UpdateTagRequest,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag = await tag_service.update_tag(tag_id, data, db)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await tag_service.delete_tag(tag_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
