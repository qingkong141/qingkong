from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# 多对多中间表（文章-标签）
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True, comment="文章ID"),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True, comment="标签ID"),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称")
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="URL标识，唯一")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="分类描述")
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True, comment="父分类ID，为空则是顶级分类")

    # 自关联（父子分类）
    parent: Mapped["Category | None"] = relationship(back_populates="children", remote_side="Category.id")
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
    posts: Mapped[list["Post"]] = relationship(back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="标签名称，唯一")
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="URL标识，唯一")
    color: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="标签颜色，如 #FF5733")

    posts: Mapped[list["Post"]] = relationship(secondary=post_tags, back_populates="tags")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="文章标题")
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="URL标识，唯一，由标题自动生成")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="文章正文，Markdown格式")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="文章摘要")
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="封面图URL")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="作者ID，关联users表")
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True, comment="分类ID，关联categories表")
    status: Mapped[str] = mapped_column(String(20), default="draft", comment="状态：draft草稿 / published已发布 / archived已归档")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="浏览次数")
    like_count: Mapped[int] = mapped_column(Integer, default=0, comment="点赞次数")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="发布时间，草稿时为空")

    # 关联关系
    author: Mapped["User"] = relationship(back_populates="posts")
    category: Mapped["Category | None"] = relationship(back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")
