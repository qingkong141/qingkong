from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentListQuery


async def list_comments(query: CommentListQuery, db: AsyncSession) -> dict:
    stmt = (
        select(Comment)
        .options(selectinload(Comment.author), selectinload(Comment.post))
    )

    if query.status:
        stmt = stmt.where(Comment.status == query.status)

    if query.post_id:
        stmt = stmt.where(Comment.post_id == query.post_id)

    if query.search:
        stmt = stmt.where(Comment.content.ilike(f"%{query.search}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    offset = (query.page - 1) * query.page_size
    stmt = stmt.order_by(Comment.created_at.desc()).offset(offset).limit(query.page_size)

    result = await db.execute(stmt)
    comments = result.scalars().all()

    return {
        "items": comments,
        "total": total,
        "page": query.page,
        "page_size": query.page_size,
    }


async def update_status(comment_id: int, new_status: str, db: AsyncSession) -> Comment | None:
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author), selectinload(Comment.post))
        .where(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        return None
    comment.status = new_status
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession) -> bool:
    comment = await db.get(Comment, comment_id)
    if not comment:
        return False
    await db.delete(comment)
    await db.commit()
    return True
