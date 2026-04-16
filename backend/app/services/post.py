import re
import random
import string
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.post import Post, Tag, post_tags
from app.schemas.post import CreatePostRequest, UpdatePostRequest, PostListQuery


def _generate_slug(title: str) -> str:
    """
    从标题生成 URL slug。
    - 提取 ASCII 字母数字，转小写，空格换成 -
    - 全中文标题（提取后为空）则用 post 作为基础
    - 末尾加 6 位随机字符保证全局唯一
    """
    base = re.sub(r'[^a-z0-9\s]', '', title.lower()).strip()
    base = re.sub(r'\s+', '-', base) or 'post'
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base}-{suffix}"


async def _load_post(post_id: int, db: AsyncSession) -> Post | None:
    """查询单篇文章，同时预加载所有关联（作者/分类/标签）"""
    result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
        )
        .where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


async def list_posts(query: PostListQuery, db: AsyncSession) -> dict:
    stmt = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
        )
    )

    # ── 筛选条件 ──────────────────────────────────────

    if query.status:
        stmt = stmt.where(Post.status == query.status)

    if query.category_id:
        stmt = stmt.where(Post.category_id == query.category_id)

    if query.tag_id:
        # 通过中间表 post_tags 过滤，避免 relationship 产生额外子查询
        stmt = stmt.join(post_tags, Post.id == post_tags.c.post_id).where(
            post_tags.c.tag_id == query.tag_id
        )

    if query.search:
        # PostgreSQL 全文搜索（FTS）
        # to_tsvector('simple', ...) 用 simple 字典，支持中文逐字分词
        # plainto_tsquery 把搜索词转成查询条件，不需要学 FTS 语法
        ts_vector = func.to_tsvector(
            'simple',
            func.coalesce(Post.title, '') + ' ' + func.coalesce(Post.content, ''),
        )
        ts_query = func.plainto_tsquery('simple', query.search)
        stmt = stmt.where(ts_vector.op('@@')(ts_query))

    # ── 先算总数，再分页 ────────────────────────────────
    # 把上面所有 where 条件带进去算 count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # 按创建时间倒序，计算偏移量
    offset = (query.page - 1) * query.page_size
    stmt = stmt.order_by(Post.created_at.desc()).offset(offset).limit(query.page_size)

    result = await db.execute(stmt)
    posts = result.scalars().all()

    return {
        "items": posts,
        "total": total,
        "page": query.page,
        "page_size": query.page_size,
    }


async def create_post(data: CreatePostRequest, author_id: int, db: AsyncSession) -> Post:
    post = Post(
        title=data.title,
        slug=_generate_slug(data.title),
        content=data.content,
        summary=data.summary,
        cover_image=data.cover_image,
        author_id=author_id,
        category_id=data.category_id,
        status=data.status,
    )

    # 创建时直接发布：记录发布时间（列为 TIMESTAMP WITHOUT TIME ZONE，用 naive UTC）
    if data.status == "published":
        post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)

    # 关联标签
    if data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        post.tags = list(result.scalars().all())

    db.add(post)
    await db.commit()

    # 重新查询以带上所有关联数据
    return await _load_post(post.id, db)


async def update_post(post_id: int, data: UpdatePostRequest, author_id: int, db: AsyncSession) -> Post:
    post = await _load_post(post_id, db)
    if not post:
        return None

    # 只有作者本人可以修改
    if post.author_id != author_id:
        raise PermissionError("无权修改此文章")

    # 逐字段更新（只更新请求中传了的字段）
    if data.title is not None:
        post.title = data.title

    if data.content is not None:
        post.content = data.content

    if data.summary is not None:
        post.summary = data.summary

    if data.cover_image is not None:
        post.cover_image = data.cover_image

    if data.category_id is not None:
        post.category_id = data.category_id

    # 状态机：切换到 published 时记录发布时间
    if data.status is not None and data.status != post.status:
        post.status = data.status
        if data.status == "published" and post.published_at is None:
            post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)

    # 更新标签关联
    if data.tag_ids is not None:
        result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        post.tags = list(result.scalars().all())

    await db.commit()
    return await _load_post(post_id, db)


async def delete_post(post_id: int, author_id: int, db: AsyncSession) -> bool:
    post = await db.get(Post, post_id)
    if not post:
        return False
    if post.author_id != author_id:
        raise PermissionError("无权删除此文章")
    await db.delete(post)
    await db.commit()
    return True


async def get_post(post_id: int, db: AsyncSession) -> Post | None:
    return await _load_post(post_id, db)
