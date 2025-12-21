"""
Тесты Kafka Consumer.

Тестирование получения сообщений из Kafka.
"""
import pytest
import uuid
import time
import allure

from src.clients.kafka_client import KafkaClient, KafkaTestHelper
from src.models.kafka import ConsumedMessage


pytestmark = pytest.mark.kafka


@allure.epic("Kafka")
@allure.feature("Consumer")
class TestKafkaConsumer:
    """Тесты Kafka Consumer."""
    
    @allure.story("Получение сообщений")
    @allure.title("Получение одного сообщения")
    @pytest.mark.smoke
    def test_consume_one_message(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        unique_group_id: str,
        sample_message: dict,
    ):
        """Тест получения одного сообщения."""
        # Отправляем сообщение
        send_result = kafka_client.send(test_topic, sample_message)
        assert send_result.success
        
        # Получаем сообщение
        received = kafka_client.consume_one(
            [test_topic],
            group_id=unique_group_id,
            timeout_ms=10000,
        )
        
        assert received is not None
        assert received.topic == test_topic
        assert received.offset >= 0
    
    @allure.story("Получение сообщений")
    @allure.title("Получение пакета сообщений")
    def test_consume_batch_messages(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        unique_group_id: str,
        batch_messages: list[dict],
    ):
        """Тест получения пакета сообщений."""
        # Отправляем пакет
        kafka_client.send_batch(test_topic, batch_messages)
        
        # Получаем пакет
        received = kafka_client.consume_batch(
            [test_topic],
            max_messages=len(batch_messages),
            group_id=unique_group_id,
            timeout_ms=15000,
        )
        
        assert len(received) == len(batch_messages)
        assert all(isinstance(m, ConsumedMessage) for m in received)
    
    @allure.story("Получение сообщений")
    @allure.title("Десериализация сообщения в dict")
    def test_consume_message_as_dict(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        unique_group_id: str,
        sample_message: dict,
    ):
        """Тест десериализации сообщения в dict."""
        kafka_client.send(test_topic, sample_message)
        
        received = kafka_client.consume_one(
            [test_topic],
            group_id=unique_group_id,
            timeout_ms=10000,
        )
        
        assert received is not None
        value_dict = received.value_as_dict()
        
        assert value_dict["id"] == sample_message["id"]
        assert value_dict["type"] == sample_message["type"]
        assert value_dict["payload"] == sample_message["payload"]
    
    @allure.story("Получение сообщений")
    @allure.title("Ожидание сообщения по условию")
    def test_consume_until_predicate(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        unique_group_id: str,
    ):
        """Тест ожидания сообщения по условию."""
        target_id = str(uuid.uuid4())
        
        # Отправляем несколько сообщений
        for i in range(3):
            kafka_client.send(test_topic, {"id": str(uuid.uuid4()), "index": i})
        
        # Отправляем целевое сообщение
        kafka_client.send(test_topic, {"id": target_id, "found": True})
        
        # Ждём конкретное сообщение
        result = kafka_client.consume_until(
            [test_topic],
            predicate=lambda m: m.value_as_dict().get("id") == target_id,
            group_id=unique_group_id,
            timeout_seconds=15.0,
        )
        
        assert result is not None
        assert result.value_as_dict()["id"] == target_id
        assert result.value_as_dict()["found"] is True
    
    @allure.story("Статистика")
    @allure.title("Проверка статистики Consumer")
    def test_consumer_stats(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        unique_group_id: str,
        sample_message: dict,
    ):
        """Тест получения статистики consumer."""
        # Отправляем и получаем сообщения
        kafka_client.send(test_topic, sample_message)
        kafka_client.consume_one([test_topic], group_id=unique_group_id)
        
        stats = kafka_client.get_consumer_stats()
        
        assert stats.messages_consumed >= 1
        assert stats.last_message_time is not None
    
    @allure.story("Таймауты")
    @allure.title("Таймаут при отсутствии сообщений")
    @pytest.mark.slow
    def test_consume_timeout_no_messages(
        self,
        kafka_client: KafkaClient,
        unique_topic: str,
        unique_group_id: str,
    ):
        """Тест таймаута когда нет сообщений в топике."""
        # Создаём пустой топик
        kafka_client.create_topic(unique_topic)
        
        start_time = time.time()
        
        result = kafka_client.consume_one(
            [unique_topic],
            group_id=unique_group_id,
            timeout_ms=3000,  # 3 секунды
        )
        
        elapsed = time.time() - start_time
        
        assert result is None
        assert elapsed >= 2.5  # Должен был подождать
        assert elapsed < 10  # Но не слишком долго
    
    @allure.story("Context Manager")
    @allure.title("Использование consumer context manager")
    def test_consumer_context_manager(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        unique_group_id: str,
        sample_message: dict,
    ):
        """Тест использования context manager для consumer."""
        kafka_client.send(test_topic, sample_message)
        
        messages = []
        with kafka_client.consumer_context([test_topic], unique_group_id) as consumer:
            for msg in consumer:
                messages.append(msg)
                break  # Получаем только первое сообщение
        
        assert len(messages) == 1
        assert messages[0].topic == test_topic






