from datetime import datetime
from pydantic import field_validator
from app.schemas.base import BaseSchema


class CommentAuthor(BaseSchema):
    id: int
    username: str
    avatar: str | None


class CommentResponse(BaseSchema):
    id: int
    post_id: int
    author_id: int
    parent_id: int | None
    content: str
    status: str
    created_at: datetime
    author: CommentAuthor
    post_title: str | None = None


class CommentListQuery(BaseSchema):
    page: int = 1
    page_size: int = 20
    status: str | None = None
    post_id: int | None = None
    search: str | None = None


class CommentListResponse(BaseSchema):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int


class UpdateCommentStatus(BaseSchema):
    status: str

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in ("pending", "approved"):
            raise ValueError("状态只能是 pending 或 approved")
        return v
