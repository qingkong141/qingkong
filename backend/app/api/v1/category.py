from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.category import CreateCategoryRequest, UpdateCategoryRequest, CategoryNode
from app.services import category as category_service

router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("", response_model=list[CategoryNode])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """返回树形结构，顶级分类在根，子分类嵌套在 children 里"""
    return await category_service.get_tree(db)


@router.post("", status_code=201)
async def create_category(
    data: CreateCategoryRequest,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        category = await category_service.create_category(data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": category.id, "name": category.name, "slug": category.slug}


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    data: UpdateCategoryRequest,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        category = await category_service.update_category(category_id, data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"id": category.id, "name": category.name, "slug": category.slug}


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await category_service.delete_category(category_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="分类不存在")
