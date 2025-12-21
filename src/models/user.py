"""Модели пользователей."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class Address(BaseModel):
    """Адрес пользователя."""
    street: str = ""
    suite: str = ""
    city: str = ""
    zipcode: str = ""
    
    model_config = ConfigDict(extra="allow")


class Company(BaseModel):
    """Компания пользователя."""
    name: str = ""
    catchPhrase: str = ""
    bs: str = ""


class UserBase(BaseModel):
    """Базовые поля пользователя."""
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class UserCreate(UserBase):
    """Модель для создания пользователя."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    phone: Optional[str] = Field(None, description="Телефон")
    website: Optional[str] = Field(None, description="Веб-сайт")


class UserUpdate(BaseModel):
    """Модель для обновления пользователя."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = None
    website: Optional[str] = None


class User(UserBase):
    """Полная модель пользователя (ответ API)."""
    id: int
    username: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[Address] = None
    company: Optional[Company] = None
    
    model_config = ConfigDict(extra="allow")


class UserResponse(BaseModel):
    """Ответ API с одним пользователем."""
    data: User


class UsersListResponse(BaseModel):
    """Ответ API со списком пользователей."""
    data: list[User]
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None


class ReqresUserData(BaseModel):
    """Данные пользователя Reqres API."""
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


class ReqresSupport(BaseModel):
    """Поддержка Reqres API."""
    url: str
    text: str


class ReqresSingleUserResponse(BaseModel):
    """Ответ Reqres API - один пользователь."""
    data: ReqresUserData
    support: ReqresSupport


class ReqresUsersListResponse(BaseModel):
    """Ответ Reqres API - список пользователей."""
    page: int
    per_page: int
    total: int
    total_pages: int
    data: list[ReqresUserData]
    support: ReqresSupport


class ReqresCreateUserRequest(BaseModel):
    """Запрос на создание пользователя Reqres API."""
    name: str
    job: str


class ReqresCreateUserResponse(BaseModel):
    """Ответ на создание пользователя Reqres API."""
    name: str
    job: str
    id: str
    createdAt: str


class ReqresUpdateUserResponse(BaseModel):
    """Ответ на обновление пользователя Reqres API."""
    name: str
    job: str
    updatedAt: str







