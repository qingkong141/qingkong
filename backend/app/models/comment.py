from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False, comment="所属文章ID，关联posts表")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="评论者ID，关联users表")
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True, comment="父评论ID，为空则是顶级评论")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="状态：pending待审核 / approved已通过")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="评论时间")

    # 关联关系
    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")
    parent: Mapped["Comment | None"] = relationship(back_populates="replies", remote_side="Comment.id")
    replies: Mapped[list["Comment"]] = relationship(back_populates="parent")
