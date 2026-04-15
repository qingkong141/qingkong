from app.schemas.base import BaseSchema


class CreateTagRequest(BaseSchema):
    name: str
    slug: str | None = None   # 不传则自动生成
    color: str | None = None  # 如 #FF5733


class UpdateTagRequest(BaseSchema):
    name: str | None = None
    slug: str | None = None
    color: str | None = None


class TagResponse(BaseSchema):
    id: int
    name: str
    slug: str
    color: str | None
