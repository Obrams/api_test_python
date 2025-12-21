"""Pydantic модели для API."""
from src.models.user import User, UserCreate, UserUpdate, UserResponse, UsersListResponse
from src.models.post import Post, PostCreate, PostUpdate, PostResponse, PostsListResponse
from src.models.comment import Comment, CommentCreate, CommentResponse
from src.models.auth import LoginRequest, RegisterRequest, AuthResponse, TokenResponse

__all__ = [
    # User
    "User",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UsersListResponse",
    # Post
    "Post",
    "PostCreate",
    "PostUpdate", 
    "PostResponse",
    "PostsListResponse",
    # Comment
    "Comment",
    "CommentCreate",
    "CommentResponse",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "AuthResponse",
    "TokenResponse",
]







