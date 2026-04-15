from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.post import CreatePostRequest, UpdatePostRequest, PostResponse, PostListResponse, PostListQuery
from app.services import post as post_service

router = APIRouter(prefix="/posts", tags=["文章"])


def _format_post(post, current_user_id: int | None = None) -> dict:
    """把 ORM Post 对象转成 dict，同时把作者头像换成代理地址"""
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "summary": post.summary,
        "cover_image": post.cover_image,
        "status": post.status,
        "view_count": post.view_count,
        "like_count": post.like_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "published_at": post.published_at,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "avatar": f"/qingkong/auth/avatar/{post.author.id}" if post.author.avatar else None,
        },
        "category": {
            "id": post.category.id,
            "name": post.category.name,
            "slug": post.category.slug,
        } if post.category else None,
        "tags": [
            {"id": t.id, "name": t.name, "slug": t.slug, "color": t.color}
            for t in post.tags
        ],
    }


@router.get("", response_model=PostListResponse)
async def list_posts(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None),
    categoryId: int | None = Query(default=None),
    tagId: int | None = Query(default=None),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    query = PostListQuery(
        page=page,
        page_size=pageSize,
        status=status,
        category_id=categoryId,
        tag_id=tagId,
        search=search,
    )
    result = await post_service.list_posts(query, db)

    # 把每篇文章的作者头像替换成代理地址
    items = [_format_post(p) for p in result["items"]]
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await post_service.create_post(data, current_user.id, db)
    return _format_post(post)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    post = await post_service.get_post(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return _format_post(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    data: UpdatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        post = await post_service.update_post(post_id, data, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return _format_post(post)


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await post_service.delete_post(post_id, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="文章不存在")
