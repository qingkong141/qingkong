import uuid
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.minio import minio_client
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import ChangePasswordRequest
from app.services import auth as auth_service



router = APIRouter(prefix="/auth", tags=["认证"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register(data, db)
        return {"id": user.id, "username": user.username, "email": user.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await auth_service.login(data, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    try:
        return await auth_service.refresh(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout", status_code=204)
async def logout(data: RefreshRequest):
    await auth_service.logout(data.refresh_token)


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """验证 get_current_user 是否生效"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar": current_user.avatar,
    }


@router.put("/password", status_code=204)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await auth_service.change_password(
            current_user, data.old_password, data.new_password, db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 只允许图片
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 生成唯一文件名
    ext = file.filename.split(".")[-1]
    filename = f"avatars/{current_user.id}/{uuid.uuid4()}.{ext}"

    # 读取文件内容上传到 MinIO
    content = await file.read()
    minio_client.put_object(
        settings.MINIO_BUCKET,
        filename,
        io.BytesIO(content),
        length=len(content),
        content_type=file.content_type,
    )

    # 拼接访问 URL 并更新数据库（用 127.0.0.1 替代 localhost，避免 VPN 问题）
    endpoint = settings.MINIO_ENDPOINT.replace("localhost", "127.0.0.1")
    avatar_url = f"http://{endpoint}/{settings.MINIO_BUCKET}/{filename}"
    user = await auth_service.update_avatar(current_user, avatar_url, db)

    return {"avatar": user.avatar}
