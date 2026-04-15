from datetime import datetime
from pydantic import BaseModel, field_validator


# ── 嵌套对象（用于 response 里的关联数据）──

class AuthorBrief(BaseModel):
    id: int
    username: str
    avatar: str | None
    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: int
    name: str
    slug: str
    model_config = {"from_attributes": True}


class TagBrief(BaseModel):
    id: int
    name: str
    slug: str
    color: str | None
    model_config = {"from_attributes": True}


# ── 创建文章 ──

class CreatePostRequest(BaseModel):
    title: str
    content: str | None = None
    summary: str | None = None
    cover_image: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = []
    status: str = "draft"

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in ("draft", "published"):
            raise ValueError("状态只能是 draft 或 published")
        return v


# ── 更新文章（所有字段可选）──

class UpdatePostRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    summary: str | None = None
    cover_image: str | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("draft", "published", "archived"):
            raise ValueError("状态只能是 draft / published / archived")
        return v


# ── 响应 ──

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str | None
    summary: str | None
    cover_image: str | None
    status: str
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    author: AuthorBrief
    category: CategoryBrief | None
    tags: list[TagBrief]

    model_config = {"from_attributes": True}
