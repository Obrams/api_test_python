"""Модели аутентификации."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Запрос на логин."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=1, description="Пароль")


class RegisterRequest(BaseModel):
    """Запрос на регистрацию."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль")
    name: Optional[str] = Field(None, description="Имя пользователя")


class AuthResponse(BaseModel):
    """Ответ аутентификации (Reqres API)."""
    id: Optional[int] = None
    token: str


class TokenResponse(BaseModel):
    """Ответ с токеном."""
    token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None


class AuthError(BaseModel):
    """Ошибка аутентификации."""
    error: str


class DummyJSONLoginRequest(BaseModel):
    """Запрос на логин DummyJSON."""
    username: str
    password: str
    expiresInMins: Optional[int] = Field(default=30)


class DummyJSONAuthResponse(BaseModel):
    """Ответ аутентификации DummyJSON."""
    id: int
    username: str
    email: str
    firstName: str
    lastName: str
    gender: str
    image: str
    accessToken: str
    refreshToken: str


class DummyJSONRefreshRequest(BaseModel):
    """Запрос на обновление токена."""
    refreshToken: str
    expiresInMins: Optional[int] = Field(default=30)







