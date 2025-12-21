"""Модели постов."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PostBase(BaseModel):
    """Базовые поля поста."""
    title: str = Field(..., min_length=1, max_length=200, description="Заголовок поста")
    body: str = Field(..., min_length=1, description="Содержимое поста")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class PostCreate(PostBase):
    """Модель для создания поста."""
    userId: int = Field(..., gt=0, description="ID автора")


class PostUpdate(BaseModel):
    """Модель для обновления поста."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1)
    userId: Optional[int] = Field(None, gt=0)


class Post(PostBase):
    """Полная модель поста."""
    id: int
    userId: int
    
    model_config = ConfigDict(extra="allow")


class PostResponse(BaseModel):
    """Ответ API с одним постом."""
    data: Post


class PostsListResponse(BaseModel):
    """Ответ API со списком постов."""
    data: list[Post]
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None


class DummyJSONPost(BaseModel):
    """Пост DummyJSON API."""
    id: int
    title: str
    body: str
    tags: list[str] = []
    reactions: dict[str, int] = {}
    views: int = 0
    userId: int


class DummyJSONPostsResponse(BaseModel):
    """Ответ DummyJSON API - список постов."""
    posts: list[DummyJSONPost]
    total: int
    skip: int
    limit: int






