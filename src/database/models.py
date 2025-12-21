"""SQLAlchemy models for database tables."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class UserDB(Base):
    """Таблица пользователей."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    posts: Mapped[list["PostDB"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["CommentDB"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<UserDB(id={self.id}, name='{self.name}', email='{self.email}')>"


class PostDB(Base):
    """Таблица постов."""
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["UserDB"]] = relationship(back_populates="posts")
    comments: Mapped[list["CommentDB"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<PostDB(id={self.id}, title='{self.title[:30]}...')>"


class CommentDB(Base):
    """Таблица комментариев."""
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    post_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("posts.id"), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post: Mapped[Optional["PostDB"]] = relationship(back_populates="comments")
    user: Mapped[Optional["UserDB"]] = relationship(back_populates="comments")
    
    def __repr__(self) -> str:
        return f"<CommentDB(id={self.id}, email='{self.email}')>"


class APILogDB(Base):
    """Таблица логов API запросов."""
    __tablename__ = "api_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request_headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    request_body: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_body: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(nullable=True)
    test_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<APILogDB(id={self.id}, {self.method} {self.url} -> {self.status_code})>"




