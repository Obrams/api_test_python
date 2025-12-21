"""
Главный conftest.py - общие фикстуры для всех тестов.
"""
import pytest
from typing import Generator, AsyncGenerator

from config.settings import settings
from src.clients.rest_client import RestClient
from src.clients.graphql_client import GraphQLClient, GraphQLClientAsync
from src.clients.grpc_client import GrpcClient
from src.clients.database_client import DatabaseClient
from src.utils.data_generator import DataGenerator, data_gen
from src.utils.logger import setup_logging
from src.models.user import UserCreate, ReqresCreateUserRequest
from src.models.post import PostCreate
from src.models.comment import CommentCreate


def pytest_configure(config):
    """Настройка pytest перед запуском тестов."""
    setup_logging(level=settings.log_level, json_format=False)


@pytest.fixture(scope="session")
def rest_client() -> Generator[RestClient, None, None]:
    """
    REST клиент для JSONPlaceholder API.
    https://jsonplaceholder.typicode.com
    """
    client = RestClient(
        base_url=settings.rest_base_url,
        timeout=settings.default_timeout,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def reqres_client() -> Generator[RestClient, None, None]:
    """
    REST клиент для Reqres API (с аутентификацией).
    https://reqres.in/api
    """
    headers = {}
    if settings.reqres_api_key:
        headers["x-api-key"] = settings.reqres_api_key
    
    client = RestClient(
        base_url=settings.reqres_base_url,
        timeout=settings.default_timeout,
        headers=headers if headers else None,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def reqres_api_key_available() -> bool:
    """Проверка наличия API ключа для Reqres."""
    return bool(settings.reqres_api_key)


@pytest.fixture(scope="session")
def httpbin_client() -> Generator[RestClient, None, None]:
    """
    REST клиент для HTTPBin API (echo).
    https://httpbin.org
    """
    client = RestClient(
        base_url=settings.httpbin_base_url,
        timeout=settings.default_timeout,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def dummyjson_client() -> Generator[RestClient, None, None]:
    """
    REST клиент для DummyJSON API.
    https://dummyjson.com
    """
    client = RestClient(
        base_url=settings.dummyjson_base_url,
        timeout=settings.default_timeout,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def graphql_countries_client() -> GraphQLClient:
    """
    GraphQL клиент для Countries API.
    https://countries.trevorblades.com/graphql
    """
    return GraphQLClient(
        endpoint=settings.graphql_countries_url,
        timeout=settings.default_timeout,
    )


@pytest.fixture(scope="session")
def graphql_spacex_client() -> GraphQLClient:
    """
    GraphQL клиент для SpaceX API.
    https://spacex-production.up.railway.app/
    """
    return GraphQLClient(
        endpoint=settings.graphql_spacex_url,
        timeout=settings.default_timeout,
    )


@pytest.fixture(scope="session")
def graphql_rickmorty_client() -> GraphQLClient:
    """
    GraphQL клиент для Rick and Morty API.
    https://rickandmortyapi.com/graphql
    """
    return GraphQLClient(
        endpoint=settings.graphql_rickmorty_url,
        timeout=settings.default_timeout,
    )


@pytest.fixture(scope="function")
async def graphql_async_client() -> AsyncGenerator[GraphQLClientAsync, None]:
    """Асинхронный GraphQL клиент."""
    client = GraphQLClientAsync(
        endpoint=settings.graphql_countries_url,
        timeout=settings.async_timeout,
    )
    yield client
    await client.aclose()


@pytest.fixture(scope="session")
def grpc_client() -> Generator[GrpcClient, None, None]:
    """
    gRPC клиент для тестового сервера.
    """
    client = GrpcClient(
        host=settings.grpc_host,
        port=settings.grpc_port,
        secure=settings.grpc_secure,
    )
    yield client
    client.close()


# =====================
# Database Fixtures
# =====================

@pytest.fixture(scope="session")
def db_client() -> Generator[DatabaseClient, None, None]:
    """
    Database клиент для PostgreSQL.
    
    Создаёт таблицы при старте сессии и удаляет при завершении.
    Для запуска PostgreSQL используйте: docker-compose up -d
    """
    client = DatabaseClient(
        database_url=settings.database_url,
        echo=settings.database_echo,
    )
    client.create_tables()
    yield client
    client.drop_tables()
    client.close()


@pytest.fixture(scope="session")
def data_generator() -> DataGenerator:
    """Генератор тестовых данных."""
    return DataGenerator()


@pytest.fixture
def random_user(data_generator: DataGenerator) -> UserCreate:
    """Случайный пользователь для создания."""
    return data_generator.user_create()


@pytest.fixture
def random_users(data_generator: DataGenerator) -> list[UserCreate]:
    """Список случайных пользователей."""
    return data_generator.users_batch(count=5)


@pytest.fixture
def reqres_user(data_generator: DataGenerator) -> ReqresCreateUserRequest:
    """Пользователь для Reqres API."""
    return data_generator.reqres_user()


@pytest.fixture
def random_post(data_generator: DataGenerator) -> PostCreate:
    """Случайный пост для создания."""
    return data_generator.post_create()


@pytest.fixture
def random_posts(data_generator: DataGenerator) -> list[PostCreate]:
    """Список случайных постов."""
    return data_generator.posts_batch(count=5)


@pytest.fixture
def random_comment(data_generator: DataGenerator) -> CommentCreate:
    """Случайный комментарий для создания."""
    return data_generator.comment_create()


@pytest.fixture(scope="session")
def auth_credentials() -> dict[str, str]:
    """Тестовые credentials для аутентификации."""
    return {
        "email": settings.test_email,
        "password": settings.test_password,
    }


@pytest.fixture(scope="session")
def invalid_credentials() -> dict[str, str]:
    """Невалидные credentials."""
    return {
        "email": "invalid@email.com",
        "password": "wrongpassword",
    }


@pytest.fixture
def valid_user_ids() -> list[int]:
    """Валидные ID пользователей для JSONPlaceholder."""
    return list(range(1, 11))


@pytest.fixture
def valid_post_ids() -> list[int]:
    """Валидные ID постов для JSONPlaceholder."""
    return list(range(1, 101))


@pytest.fixture
def valid_comment_ids() -> list[int]:
    """Валидные ID комментариев для JSONPlaceholder."""
    return list(range(1, 501))


@pytest.fixture
def country_codes() -> list[str]:
    """Валидные коды стран для GraphQL Countries API."""
    return ["US", "RU", "DE", "FR", "JP", "CN", "GB", "BR", "IN", "CA"]


def pytest_collection_modifyitems(items):
    """Автоматическое добавление маркеров на основе пути файла."""
    for item in items:
        if "/rest/" in str(item.fspath):
            item.add_marker(pytest.mark.rest)
        elif "/graphql/" in str(item.fspath):
            item.add_marker(pytest.mark.graphql)
        elif "/grpc/" in str(item.fspath):
            item.add_marker(pytest.mark.grpc)
        elif "/database/" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        elif "/kafka/" in str(item.fspath):
            item.add_marker(pytest.mark.kafka)






