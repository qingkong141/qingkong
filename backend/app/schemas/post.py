from datetime import datetime
from pydantic import field_validator
from app.schemas.base import BaseSchema


class AuthorBrief(BaseSchema):
    id: int
    username: str
    avatar: str | None


class CategoryBrief(BaseSchema):
    id: int
    name: str
    slug: str


class TagBrief(BaseSchema):
    id: int
    name: str
    slug: str
    color: str | None


class CreatePostRequest(BaseSchema):
    title: str
    content: str | None = None
    summary: str | None = None
    cover_image: str | None = None   # → coverImage
    category_id: int | None = None   # → categoryId
    tag_ids: list[int] = []          # → tagIds
    status: str = "draft"

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in ("draft", "published"):
            raise ValueError("状态只能是 draft 或 published")
        return v


class UpdatePostRequest(BaseSchema):
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


class PostListQuery(BaseSchema):
    """列表查询参数（URL query string）"""
    page: int = 1
    page_size: int = 10          # → pageSize
    status: str | None = None
    category_id: int | None = None  # → categoryId
    tag_id: int | None = None       # → tagId
    search: str | None = None       # 全文搜索关键词


class PostSummary(BaseSchema):
    """列表用的精简格式，不含正文 content（content 可能很大）"""
    id: int
    title: str
    slug: str
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


class PostListResponse(BaseSchema):
    items: list[PostSummary]
    total: int
    page: int
    page_size: int               # → pageSize


class PostResponse(BaseSchema):
    id: int
    title: str
    slug: str
    content: str | None
    summary: str | None
    cover_image: str | None          # → coverImage
    status: str
    view_count: int                  # → viewCount
    like_count: int                  # → likeCount
    created_at: datetime             # → createdAt
    updated_at: datetime             # → updatedAt
    published_at: datetime | None    # → publishedAt
    author: AuthorBrief
    category: CategoryBrief | None
    tags: list[TagBrief]
