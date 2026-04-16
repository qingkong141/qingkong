from datetime import datetime
from app.schemas.base import BaseSchema


class FileResponse(BaseSchema):
    id: int
    name: str
    path: str
    parent_id: int | None
    size: int
    mime_type: str | None
    storage_key: str | None
    md5: str | None
    owner_id: int
    is_dir: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class CreateFolderRequest(BaseSchema):
    name: str
    parent_id: int | None = None


class RenameRequest(BaseSchema):
    name: str


class MoveRequest(BaseSchema):
    parent_id: int | None = None


class MultipartInitRequest(BaseSchema):
    filename: str
    total_size: int
    total_chunks: int
    parent_id: int | None = None


class CreateShareRequest(BaseSchema):
    file_id: int
    password: str | None = None
    expire_hours: int | None = None


class ShareResponse(BaseSchema):
    id: int
    file_id: int
    token: str
    has_password: bool
    expire_at: datetime | None
    download_count: int
    created_at: datetime
    file_name: str
    file_size: int
    is_dir: bool


class ShareAccessRequest(BaseSchema):
    password: str | None = None
