import re
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.post import Tag
from app.schemas.tag import CreateTagRequest, UpdateTagRequest


def _generate_slug(name: str) -> str:
    base = re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()
    base = re.sub(r'\s+', '-', base) or 'tag'
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base}-{suffix}"


async def list_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


async def create_tag(data: CreateTagRequest, db: AsyncSession) -> Tag:
    # 名称唯一检查
    existing = await db.execute(select(Tag).where(Tag.name == data.name))
    if existing.scalar_one_or_none():
        raise ValueError("标签名称已存在")

    tag = Tag(
        name=data.name,
        slug=data.slug or _generate_slug(data.name),
        color=data.color,
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def update_tag(tag_id: int, data: UpdateTagRequest, db: AsyncSession) -> Tag:
    tag = await db.get(Tag, tag_id)
    if not tag:
        return None

    if data.name is not None:
        tag.name = data.name
    if data.slug is not None:
        tag.slug = data.slug
    if data.color is not None:
        tag.color = data.color

    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(tag_id: int, db: AsyncSession) -> bool:
    tag = await db.get(Tag, tag_id)
    if not tag:
        return False
    # post_tags 中间表的记录会随标签删除自动级联清理（ForeignKey 默认行为）
    await db.delete(tag)
    await db.commit()
    return True
