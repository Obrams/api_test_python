"""Генератор тестовых данных на базе Faker."""
from typing import Any
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from src.models.user import UserCreate, User, ReqresCreateUserRequest
from src.models.post import PostCreate, Post
from src.models.comment import CommentCreate


# Инициализация Faker с локализацией
fake = Faker(["en_US", "ru_RU"])


class DataGenerator:
    """Генератор тестовых данных для API."""
    
    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
    
    def user_create(self, **overrides: Any) -> UserCreate:
        """Сгенерировать данные для создания пользователя."""
        data = {
            "name": self.fake.name(),
            "email": self.fake.email(),
            "username": self.fake.user_name(),
            "phone": self.fake.phone_number(),
            "website": self.fake.url(),
        }
        data.update(overrides)
        return UserCreate(**data)
    
    def reqres_user(self, **overrides: Any) -> ReqresCreateUserRequest:
        """Сгенерировать данные для Reqres API."""
        data = {
            "name": self.fake.name(),
            "job": self.fake.job(),
        }
        data.update(overrides)
        return ReqresCreateUserRequest(**data)
    
    def users_batch(self, count: int = 10, **overrides: Any) -> list[UserCreate]:
        """Сгенерировать пачку пользователей."""
        return [self.user_create(**overrides) for _ in range(count)]
    
    def post_create(self, user_id: int = 1, **overrides: Any) -> PostCreate:
        """Сгенерировать данные для создания поста."""
        data = {
            "title": self.fake.sentence(nb_words=6),
            "body": self.fake.paragraph(nb_sentences=5),
            "userId": user_id,
        }
        data.update(overrides)
        return PostCreate(**data)
    
    def posts_batch(
        self,
        count: int = 10,
        user_id: int | None = None,
        **overrides: Any,
    ) -> list[PostCreate]:
        """Сгенерировать пачку постов."""
        return [
            self.post_create(
                user_id=user_id or self.fake.random_int(min=1, max=10),
                **overrides,
            )
            for _ in range(count)
        ]
    
    def comment_create(self, post_id: int = 1, **overrides: Any) -> CommentCreate:
        """Сгенерировать данные для создания комментария."""
        data = {
            "name": self.fake.sentence(nb_words=4),
            "body": self.fake.paragraph(nb_sentences=3),
            "email": self.fake.email(),
            "postId": post_id,
        }
        data.update(overrides)
        return CommentCreate(**data)
    
    def comments_batch(
        self,
        count: int = 10,
        post_id: int | None = None,
        **overrides: Any,
    ) -> list[CommentCreate]:
        """Сгенерировать пачку комментариев."""
        return [
            self.comment_create(
                post_id=post_id or self.fake.random_int(min=1, max=100),
                **overrides,
            )
            for _ in range(count)
        ]
    
    def email(self) -> str:
        """Случайный email."""
        return self.fake.email()
    
    def name(self) -> str:
        """Случайное имя."""
        return self.fake.name()
    
    def username(self) -> str:
        """Случайный username."""
        return self.fake.user_name()
    
    def text(self, length: int = 100) -> str:
        """Случайный текст заданной длины."""
        return self.fake.text(max_nb_chars=length)
    
    def sentence(self, words: int = 6) -> str:
        """Случайное предложение."""
        return self.fake.sentence(nb_words=words)
    
    def paragraph(self, sentences: int = 3) -> str:
        """Случайный параграф."""
        return self.fake.paragraph(nb_sentences=sentences)
    
    def uuid(self) -> str:
        """Случайный UUID."""
        return str(self.fake.uuid4())
    
    def int_in_range(self, min_val: int = 1, max_val: int = 100) -> int:
        """Случайное целое число в диапазоне."""
        return self.fake.random_int(min=min_val, max=max_val)
    
    def boolean(self) -> bool:
        """Случайный boolean."""
        return self.fake.boolean()
    
    def url(self) -> str:
        """Случайный URL."""
        return self.fake.url()
    
    def phone(self) -> str:
        """Случайный телефон."""
        return self.fake.phone_number()
    
    def country_code(self) -> str:
        """Случайный код страны (ISO 3166-1 alpha-2)."""
        return self.fake.country_code()


class UserCreateFactory(ModelFactory):
    """Фабрика для UserCreate."""
    __model__ = UserCreate


class PostCreateFactory(ModelFactory):
    """Фабрика для PostCreate."""
    __model__ = PostCreate


class CommentCreateFactory(ModelFactory):
    """Фабрика для CommentCreate."""
    __model__ = CommentCreate


# Глобальный экземпляр генератора
data_gen = DataGenerator()






