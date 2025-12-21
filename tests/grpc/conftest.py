"""Фикстуры специфичные для gRPC тестов."""
import pytest


@pytest.fixture
def hello_request_data():
    """Данные для HelloRequest."""
    return {"name": "World"}


@pytest.fixture
def empty_request_data():
    """Пустые данные для запроса."""
    return {}


@pytest.fixture
def grpc_metadata():
    """Metadata для gRPC запросов."""
    return [
        ("x-custom-header", "test-value"),
        ("x-request-id", "12345"),
    ]







