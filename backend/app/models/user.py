from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名，唯一")
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="邮箱，唯一")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="bcrypt加密后的密码")
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="头像URL")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, comment="个人简介")
    storage_used: Mapped[int] = mapped_column(BigInteger, default=0, comment="已用存储空间，单位字节")
    storage_quota: Mapped[int] = mapped_column(BigInteger, default=5 * 1024 * 1024 * 1024, comment="存储配额，默认5GB，单位字节")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

    # 关联关系
    posts: Mapped[list["Post"]] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
    files: Mapped[list["File"]] = relationship(back_populates="owner")
