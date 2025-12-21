"""Модели комментариев."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class CommentBase(BaseModel):
    """Базовые поля комментария."""
    name: str = Field(..., min_length=1, max_length=200, description="Название комментария")
    body: str = Field(..., min_length=1, description="Текст комментария")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class CommentCreate(CommentBase):
    """Модель для создания комментария."""
    postId: int = Field(..., gt=0, description="ID поста")
    email: EmailStr = Field(..., description="Email автора")


class Comment(CommentBase):
    """Полная модель комментария."""
    id: int
    postId: int
    email: str
    
    model_config = ConfigDict(extra="allow")


class CommentResponse(BaseModel):
    """Ответ API с одним комментарием."""
    data: Comment


class CommentsListResponse(BaseModel):
    """Ответ API со списком комментариев."""
    data: list[Comment]
    total: Optional[int] = None


class DummyJSONCommentUser(BaseModel):
    """Пользователь комментария DummyJSON."""
    id: int
    username: str
    fullName: str


class DummyJSONComment(BaseModel):
    """Комментарий DummyJSON API."""
    id: int
    body: str
    postId: int
    likes: int = 0
    user: DummyJSONCommentUser


class DummyJSONCommentsResponse(BaseModel):
    """Ответ DummyJSON API - список комментариев."""
    comments: list[DummyJSONComment]
    total: int
    skip: int
    limit: int







