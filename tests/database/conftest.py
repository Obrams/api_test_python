"""
Database test fixtures.
"""
import pytest
from typing import Generator

from src.clients.database_client import DatabaseClient


@pytest.fixture(autouse=True)
def clean_db_tables(db_client: DatabaseClient) -> Generator[None, None, None]:
    """
    Очистка таблиц после каждого теста.
    
    Автоматически применяется ко всем тестам в директории database/.
    """
    yield
    # Cleanup после теста
    db_client.truncate_all()


@pytest.fixture
def db_with_user(db_client: DatabaseClient) -> dict:
    """
    Фикстура с предсозданным пользователем в БД.
    
    Returns:
        Данные созданного пользователя
    """
    user_data = {
        "id": 999,
        "name": "Test User",
        "email": "test@example.com",
        "username": "testuser",
    }
    db_client.save_user(user_data)
    return user_data


@pytest.fixture
def db_with_post(db_client: DatabaseClient) -> dict:
    """
    Фикстура с предсозданным постом в БД.
    
    Returns:
        Данные созданного поста
    """
    post_data = {
        "id": 999,
        "userId": 1,
        "title": "Test Post Title",
        "body": "Test post body content.",
    }
    db_client.save_post(post_data)
    return post_data




