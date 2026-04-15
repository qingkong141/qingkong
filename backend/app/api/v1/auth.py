from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
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
    }
