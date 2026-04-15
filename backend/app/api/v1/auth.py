import uuid
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.minio import minio_client
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserMeResponse
from app.schemas.user import ChangePasswordRequest
from app.services import auth as auth_service



router = APIRouter(prefix="/auth", tags=["认证"])


class RefreshRequest(BaseSchema):
    refresh_token: str  # 接收 refreshToken 或 refresh_token 均可


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


@router.get("/me", response_model=UserMeResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserMeResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar=f"/qingkong/auth/avatar/{current_user.id}" if current_user.avatar else None,
    )


@router.get("/avatar/{user_id}")
async def get_avatar(user_id: int, db: AsyncSession = Depends(get_db)):
    """头像代理：从 MinIO 取图片流式返回，不暴露 MinIO 地址"""
    user = await db.get(User, user_id)
    if not user or not user.avatar:
        raise HTTPException(status_code=404, detail="头像不存在")

    # 从存储的完整 URL 中提取 MinIO object 路径
    # 例：http://127.0.0.1:9000/qingkong/avatars/1/xxx.jpg → avatars/1/xxx.jpg
    bucket_prefix = f"/{settings.MINIO_BUCKET}/"
    idx = user.avatar.find(bucket_prefix)
    if idx == -1:
        raise HTTPException(status_code=404, detail="头像地址格式异常")
    object_name = user.avatar[idx + len(bucket_prefix):]

    # 从 MinIO 读取图片并流式返回
    response = minio_client.get_object(settings.MINIO_BUCKET, object_name)
    media_type = response.headers.get("content-type", "image/jpeg")
    return StreamingResponse(response, media_type=media_type)


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
