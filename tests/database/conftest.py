"""Фикстуры для тестов БД."""
import pytest
from src.clients.rest_client import RestClient
from src.clients.database_client import DatabaseClient


@pytest.fixture
def db_with_user(
    rest_client: RestClient,
    db_client: DatabaseClient,
    random_user,
) -> dict:
    """Фикстура создаёт пользователя через API и сохраняет в БД."""
    response = rest_client.post("/users", json=random_user.model_dump())
    api_user = response.json()
    db_client.save_user(api_user)
    return api_user
