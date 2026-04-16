from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件或文件夹名称")
    path: Mapped[str] = mapped_column(Text, nullable=False, comment="完整路径，如 /我的文档/图片")
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("files.id"), nullable=True, comment="父文件夹ID，为空则在根目录")
    size: Mapped[int] = mapped_column(BigInteger, default=0, comment="文件大小，单位字节，文件夹为0")
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="文件类型，如 image/png、video/mp4")
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="MinIO中的存储路径，文件夹为空")
    md5: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="文件MD5，用于秒传判断，文件夹为空")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="所有者ID，关联users表")
    is_dir: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为文件夹")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已删除（软删除，进入回收站）")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

    # 关联关系
    owner: Mapped["User"] = relationship(back_populates="files")
    parent: Mapped["File | None"] = relationship(back_populates="children", remote_side="File.id")
    children: Mapped[list["File"]] = relationship(back_populates="parent")
    shares: Mapped[list["Share"]] = relationship(back_populates="file")


class Share(Base):
    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    file_id: Mapped[int] = mapped_column(Integer, ForeignKey("files.id"), nullable=False, comment="分享的文件ID，关联files表")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="分享者ID，关联users表")
    token: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="分享短码，唯一，用于生成分享链接")
    password: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="提取密码，为空则无需密码")
    expire_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="过期时间，为空则永不过期")
    download_count: Mapped[int] = mapped_column(Integer, default=0, comment="下载次数统计")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")

    file: Mapped["File"] = relationship(back_populates="shares")
    owner: Mapped["User"] = relationship()
