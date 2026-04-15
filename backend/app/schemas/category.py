from __future__ import annotations
from app.schemas.base import BaseSchema


class CreateCategoryRequest(BaseSchema):
    name: str
    slug: str | None = None       # 不传则自动生成
    description: str | None = None
    parent_id: int | None = None  # → parentId，为空则是顶级分类


class UpdateCategoryRequest(BaseSchema):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    parent_id: int | None = None


class CategoryNode(BaseSchema):
    """单个分类节点，含子分类（树结构）"""
    id: int
    name: str
    slug: str
    description: str | None
    parent_id: int | None         # → parentId
    children: list[CategoryNode] = []


# Pydantic v2 自引用模型需要调用 model_rebuild()
CategoryNode.model_rebuild()
