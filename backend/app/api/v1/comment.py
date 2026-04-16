from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.comment import (
    CommentListResponse,
    CommentResponse,
    CommentListQuery,
    UpdateCommentStatus,
)
from app.services import comment as comment_service

router = APIRouter(prefix="/comments", tags=["评论"])


def _format_comment(c) -> dict:
    return {
        "id": c.id,
        "post_id": c.post_id,
        "author_id": c.author_id,
        "parent_id": c.parent_id,
        "content": c.content,
        "status": c.status,
        "created_at": c.created_at,
        "author": {
            "id": c.author.id,
            "username": c.author.username,
            "avatar": f"/qingkong/auth/avatar/{c.author.id}" if c.author.avatar else None,
        },
        "post_title": c.post.title if c.post else None,
    }


@router.get("", response_model=CommentListResponse)
async def list_comments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    status: str | None = Query(default=None),
    post_id: int | None = Query(default=None, alias="postId"),
    search: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = CommentListQuery(
        page=page,
        page_size=page_size,
        status=status,
        post_id=post_id,
        search=search,
    )
    result = await comment_service.list_comments(query, db)
    items = [_format_comment(c) for c in result["items"]]
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.put("/{comment_id}/status", response_model=CommentResponse)
async def update_comment_status(
    comment_id: int,
    data: UpdateCommentStatus,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    comment = await comment_service.update_status(comment_id, data.status, db)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return _format_comment(comment)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await comment_service.delete_comment(comment_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="评论不存在")
