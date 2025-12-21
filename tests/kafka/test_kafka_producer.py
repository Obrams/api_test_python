"""
Тесты Kafka Producer.

Тестирование отправки сообщений в Kafka.
"""
import pytest
import uuid
import allure

from src.clients.kafka_client import KafkaClient
from src.models.kafka import (
    UserEventMessage,
    OrderEventMessage,
    MetricMessage,
    ProducerResult,
    MessagePriority,
)


@allure.epic("Kafka")
@allure.feature("Producer")
@pytest.mark.kafka
class TestKafkaProducer:
    """Тесты Kafka Producer."""
    
    @allure.story("Отправка сообщений")
    @allure.title("Отправка простого сообщения")
    @pytest.mark.smoke
    def test_send_simple_message(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        sample_message: dict,
    ):
        """Тест отправки простого dict сообщения."""
        result = kafka_client.send(test_topic, sample_message)
        
        assert result.success is True
        assert result.topic == test_topic
        assert result.partition >= 0
        assert result.offset >= 0
        assert result.error is None
    
    @allure.story("Отправка сообщений")
    @allure.title("Отправка сообщения с ключом")
    def test_send_message_with_key(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        sample_message: dict,
    ):
        """Тест отправки сообщения с ключом партиционирования."""
        key = f"user_{uuid.uuid4().hex[:8]}"
        result = kafka_client.send(test_topic, sample_message, key=key)
        
        assert result.success is True
        assert result.topic == test_topic
        assert result.offset >= 0
    
    @allure.story("Отправка сообщений")
    @allure.title("Отправка Pydantic модели")
    def test_send_pydantic_model(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        user_event_message: UserEventMessage,
    ):
        """Тест отправки Pydantic модели напрямую."""
        result = kafka_client.send(test_topic, user_event_message)
        
        assert result.success is True
        assert result.topic == test_topic
        assert result.timestamp is not None
    
    @allure.story("Отправка сообщений")
    @allure.title("Отправка OrderEventMessage")
    def test_send_order_event(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        order_event_message: OrderEventMessage,
    ):
        """Тест отправки события заказа."""
        result = kafka_client.send(
            test_topic,
            order_event_message,
            key=order_event_message.order_id,
        )
        
        assert result.success is True
        assert result.partition >= 0
    
    @allure.story("Отправка сообщений")
    @allure.title("Отправка MetricMessage")
    def test_send_metric_message(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        metric_message: MetricMessage,
    ):
        """Тест отправки метрики."""
        result = kafka_client.send(test_topic, metric_message)
        
        assert result.success is True
        assert result.topic == test_topic
    
    @allure.story("Batch операции")
    @allure.title("Отправка пакета сообщений")
    def test_send_batch_messages(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        batch_messages: list[dict],
    ):
        """Тест batch отправки сообщений."""
        results = kafka_client.send_batch(test_topic, batch_messages)
        
        assert len(results) == len(batch_messages)
        assert all(r.success for r in results)
        
        # Проверяем что offset увеличивается
        offsets = [r.offset for r in results]
        assert offsets == sorted(offsets)
    
    @allure.story("Статистика")
    @allure.title("Проверка статистики Producer")
    def test_producer_stats(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        sample_message: dict,
    ):
        """Тест получения статистики producer."""
        initial_stats = kafka_client.get_producer_stats()
        initial_count = initial_stats.messages_sent
        
        # Отправляем несколько сообщений
        for _ in range(3):
            kafka_client.send(test_topic, sample_message)
        
        stats = kafka_client.get_producer_stats()
        
        assert stats.messages_sent >= initial_count + 3
        assert test_topic in stats.topics
        assert stats.last_send_time is not None





