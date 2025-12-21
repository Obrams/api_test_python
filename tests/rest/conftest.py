"""Фикстуры специфичные для REST тестов."""
import pytest


@pytest.fixture
def posts_endpoint() -> str:
    """Endpoint постов."""
    return "/posts"


@pytest.fixture
def users_endpoint() -> str:
    """Endpoint пользователей."""
    return "/users"


@pytest.fixture  
def comments_endpoint() -> str:
    """Endpoint комментариев."""
    return "/comments"


@pytest.fixture
def albums_endpoint() -> str:
    """Endpoint альбомов."""
    return "/albums"


@pytest.fixture
def photos_endpoint() -> str:
    """Endpoint фото."""
    return "/photos"


@pytest.fixture
def todos_endpoint() -> str:
    """Endpoint todos."""
    return "/todos"






