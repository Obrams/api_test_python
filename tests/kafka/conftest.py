"""
Фикстуры для Kafka тестов.
"""
import pytest
import uuid
from typing import Generator

from config.settings import settings
from src.clients.kafka_client import KafkaClient, KafkaTestHelper
from src.models.kafka import (
    UserEventMessage,
    OrderEventMessage,
    NotificationMessage,
    MetricMessage,
    LogMessage,
    CommandMessage,
    MessagePriority,
    MessageType,
)
from src.utils.data_generator import DataGenerator


@pytest.fixture(scope="session")
def kafka_client() -> Generator[KafkaClient, None, None]:
    """
    Kafka клиент для тестов.
    
    Для запуска Kafka используйте: docker-compose up -d
    """
    client = KafkaClient(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id="pytest_kafka_client",
        timeout_ms=settings.kafka_timeout_ms,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def kafka_helper(kafka_client: KafkaClient) -> KafkaTestHelper:
    """Helper для тестирования Kafka."""
    return KafkaTestHelper(kafka_client)


@pytest.fixture
def unique_topic() -> str:
    """Генерирует уникальное имя топика для теста."""
    return f"test_topic_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_topic(kafka_client: KafkaClient, unique_topic: str) -> Generator[str, None, None]:
    """Создаёт топик для теста и удаляет после."""
    kafka_client.create_topic(unique_topic, num_partitions=1)
    yield unique_topic
    try:
        kafka_client.delete_topic(unique_topic)
    except Exception:
        pass  # Игнорируем ошибки удаления


@pytest.fixture
def test_topic_multi_partition(kafka_client: KafkaClient) -> Generator[str, None, None]:
    """Топик с несколькими партициями."""
    topic_name = f"test_multi_partition_{uuid.uuid4().hex[:8]}"
    kafka_client.create_topic(topic_name, num_partitions=3)
    yield topic_name
    try:
        kafka_client.delete_topic(topic_name)
    except Exception:
        pass


@pytest.fixture
def unique_group_id() -> str:
    """Генерирует уникальный group_id для consumer."""
    return f"test_group_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_message() -> dict:
    """Простое тестовое сообщение."""
    return {
        "id": str(uuid.uuid4()),
        "type": "test",
        "payload": {"key": "value", "number": 42},
        "timestamp": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_messages() -> list[dict]:
    """Список тестовых сообщений."""
    return [
        {"id": i, "message": f"Test message {i}", "data": {"index": i}}
        for i in range(10)
    ]


@pytest.fixture
def user_event_message(data_generator: DataGenerator) -> UserEventMessage:
    """Событие пользователя."""
    return UserEventMessage(
        user_id=data_generator.fake.random_int(min=1, max=10000),
        action="user_registered",
        details={
            "email": data_generator.fake.email(),
            "username": data_generator.fake.user_name(),
        },
        ip_address=data_generator.fake.ipv4(),
        user_agent=data_generator.fake.user_agent(),
    )


@pytest.fixture
def order_event_message(data_generator: DataGenerator) -> OrderEventMessage:
    """Событие заказа."""
    return OrderEventMessage(
        order_id=str(uuid.uuid4()),
        user_id=data_generator.fake.random_int(min=1, max=10000),
        status="created",
        total_amount=data_generator.fake.pyfloat(min_value=10, max_value=1000, right_digits=2),
        currency="USD",
        items=[
            {
                "product_id": str(uuid.uuid4()),
                "name": data_generator.fake.word(),
                "quantity": data_generator.fake.random_int(min=1, max=5),
                "price": data_generator.fake.pyfloat(min_value=5, max_value=200, right_digits=2),
            }
            for _ in range(data_generator.fake.random_int(min=1, max=5))
        ],
    )


@pytest.fixture
def notification_message(data_generator: DataGenerator) -> NotificationMessage:
    """Уведомление."""
    return NotificationMessage(
        recipient_id=data_generator.fake.random_int(min=1, max=10000),
        channel="email",
        subject=data_generator.fake.sentence(),
        body=data_generator.fake.paragraph(),
        template_id="welcome_email",
        variables={
            "user_name": data_generator.fake.name(),
            "activation_link": data_generator.fake.url(),
        },
    )


@pytest.fixture
def metric_message(data_generator: DataGenerator) -> MetricMessage:
    """Метрика."""
    return MetricMessage(
        metric_name="api_response_time",
        value=data_generator.fake.pyfloat(min_value=0.01, max_value=5.0, right_digits=3),
        unit="seconds",
        tags={
            "endpoint": "/api/users",
            "method": "GET",
            "status_code": "200",
        },
    )


@pytest.fixture
def log_message(data_generator: DataGenerator) -> LogMessage:
    """Лог сообщение."""
    return LogMessage(
        level="info",
        logger_name="api.service",
        message=data_generator.fake.sentence(),
        context={
            "request_id": str(uuid.uuid4()),
            "user_id": data_generator.fake.random_int(min=1, max=10000),
        },
    )


@pytest.fixture
def command_message(data_generator: DataGenerator) -> CommandMessage:
    """Команда."""
    return CommandMessage(
        command_name="process_order",
        payload={
            "order_id": str(uuid.uuid4()),
            "action": "validate_payment",
        },
        reply_to="order_responses",
    )


@pytest.fixture
def high_priority_message() -> dict:
    """Сообщение с высоким приоритетом."""
    return {
        "id": str(uuid.uuid4()),
        "priority": MessagePriority.HIGH.value,
        "type": MessageType.NOTIFICATION.value,
        "content": "Urgent notification",
        "requires_ack": True,
    }


@pytest.fixture
def batch_messages() -> list[dict]:
    """Пакет сообщений для batch тестов."""
    return [
        {
            "batch_id": str(uuid.uuid4()),
            "sequence": i,
            "payload": f"Batch message {i}",
        }
        for i in range(5)
    ]


@pytest.fixture(scope="session")
def data_generator() -> DataGenerator:
    """Генератор тестовых данных."""
    return DataGenerator()





