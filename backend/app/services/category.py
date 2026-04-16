import re
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.post import Category
from app.schemas.category import CreateCategoryRequest, UpdateCategoryRequest


def _generate_slug(name: str) -> str:
    base = re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()
    base = re.sub(r'\s+', '-', base) or 'category'
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base}-{suffix}"


async def get_tree(db: AsyncSession) -> list[dict]:
    """
    一次查出所有分类，在 Python 内存中拼成树。
    比递归查库高效：只有 1 次 SQL。
    """
    result = await db.execute(select(Category))
    all_cats = result.scalars().all()

    # 先把所有分类变成 dict，方便追加 children
    node_map: dict[int, dict] = {
        c.id: {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "parent_id": c.parent_id,
            "children": [],
        }
        for c in all_cats
    }

    roots = []
    for node in node_map.values():
        pid = node["parent_id"]
        if pid is None:
            roots.append(node)
        elif pid in node_map:
            node_map[pid]["children"].append(node)

    return roots


async def get_by_slug(slug: str, db: AsyncSession) -> Category | None:
    result = await db.execute(select(Category).where(Category.slug == slug))
    return result.scalar_one_or_none()


async def create_category(data: CreateCategoryRequest, db: AsyncSession) -> Category:
    # 检查父分类是否存在
    if data.parent_id:
        parent = await db.get(Category, data.parent_id)
        if not parent:
            raise ValueError("父分类不存在")

    slug = data.slug or _generate_slug(data.name)

    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
        parent_id=data.parent_id,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(category_id: int, data: UpdateCategoryRequest, db: AsyncSession) -> Category:
    category = await db.get(Category, category_id)
    if not category:
        return None

    if data.name is not None:
        category.name = data.name
    if data.slug is not None:
        category.slug = data.slug
    if data.description is not None:
        category.description = data.description
    if data.parent_id is not None:
        # 防止把自己设为自己的父分类
        if data.parent_id == category_id:
            raise ValueError("不能将自身设为父分类")
        parent = await db.get(Category, data.parent_id)
        if not parent:
            raise ValueError("父分类不存在")
        category.parent_id = data.parent_id

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(category_id: int, db: AsyncSession) -> bool:
    category = await db.get(Category, category_id)
    if not category:
        return False

    # 有子分类时拒绝删除，防止数据孤立
    result = await db.execute(
        select(Category).where(Category.parent_id == category_id).limit(1)
    )
    if result.scalar_one_or_none():
        raise ValueError("该分类下存在子分类，请先删除子分类")

    await db.delete(category)
    await db.commit()
    return True
