"""
Kafka клиент с поддержкой sync/async операций для тестирования.
"""
from typing import Any, Callable, Generator
import json
import time
from datetime import datetime, UTC
from contextlib import contextmanager

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError
from pydantic import BaseModel
import structlog

from src.models.kafka import (
    ProducerResult,
    ConsumedMessage,
    ConsumerStats,
    ProducerStats,
)

logger = structlog.get_logger(__name__)


class KafkaClient:
    """Kafka клиент с поддержкой Producer и Consumer операций."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = "api_test_client",
        timeout_ms: int = 30000,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.timeout_ms = timeout_ms
        
        self._producer: KafkaProducer | None = None
        self._consumer: KafkaConsumer | None = None
        self._admin_client: KafkaAdminClient | None = None
        
        self._producer_stats = ProducerStats()
        self._consumer_stats = ConsumerStats()
        
        logger.info(
            "Kafka client initialized",
            bootstrap_servers=self.bootstrap_servers,
            client_id=self.client_id,
        )
    
    # =====================
    # Admin Operations
    # =====================
    
    @property
    def admin_client(self) -> KafkaAdminClient:
        """Lazy initialization admin клиента."""
        if self._admin_client is None:
            self._admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}_admin",
            )
        return self._admin_client
    
    def create_topic(
        self,
        topic: str,
        num_partitions: int = 1,
        replication_factor: int = 1,
    ) -> bool:
        """Создать топик."""
        try:
            new_topic = NewTopic(
                name=topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )
            self.admin_client.create_topics([new_topic])
            logger.info("Topic created", topic=topic, partitions=num_partitions)
            return True
        except TopicAlreadyExistsError:
            logger.debug("Topic already exists", topic=topic)
            return True
        except KafkaError as e:
            logger.error("Failed to create topic", topic=topic, error=str(e))
            return False
    
    def delete_topic(self, topic: str) -> bool:
        """Удалить топик."""
        try:
            self.admin_client.delete_topics([topic])
            logger.info("Topic deleted", topic=topic)
            return True
        except KafkaError as e:
            logger.error("Failed to delete topic", topic=topic, error=str(e))
            return False
    
    def list_topics(self) -> list[str]:
        """Получить список топиков."""
        try:
            metadata = self.admin_client.list_topics()
            return list(metadata)
        except KafkaError as e:
            logger.error("Failed to list topics", error=str(e))
            return []
    
    def topic_exists(self, topic: str) -> bool:
        """Проверить существование топика."""
        return topic in self.list_topics()
    
    def is_available(self) -> bool:
        """Проверить доступность Kafka брокеров."""
        try:
            admin = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}_health_check",
                request_timeout_ms=5000,
            )
            admin.list_topics()
            admin.close()
            return True
        except Exception as e:
            logger.debug("Kafka brokers not available", error=str(e))
            return False
    
    # =====================
    # Producer Operations
    # =====================
    
    @property
    def producer(self) -> KafkaProducer:
        """Lazy initialization producer."""
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}_producer",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                max_block_ms=self.timeout_ms,
            )
        return self._producer
    
    def _serialize_value(self, value: dict | BaseModel) -> dict:
        """Сериализация значения."""
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        return value
    
    def send(
        self,
        topic: str,
        value: dict | BaseModel,
        key: str | None = None,
        headers: list[tuple[str, bytes]] | None = None,
        partition: int | None = None,
    ) -> ProducerResult:
        """Отправить сообщение (синхронно)."""
        try:
            serialized_value = self._serialize_value(value)
            
            future = self.producer.send(
                topic=topic,
                value=serialized_value,
                key=key,
                headers=headers,
                partition=partition,
            )
            
            # Ждём подтверждения
            record_metadata = future.get(timeout=self.timeout_ms / 1000)
            
            result = ProducerResult(
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset,
                timestamp=datetime.fromtimestamp(record_metadata.timestamp / 1000),
                success=True,
            )
            
            # Обновляем статистику
            self._producer_stats.messages_sent += 1
            self._producer_stats.last_send_time = datetime.now(UTC)
            topics_list: list[str] = self._producer_stats.topics
            if topic not in topics_list:
                topics_list.append(topic)
            
            logger.debug(
                "Message sent",
                topic=topic,
                partition=result.partition,
                offset=result.offset,
            )
            return result
            
        except Exception as e:
            self._producer_stats.messages_failed += 1
            logger.error("Failed to send message", topic=topic, error=str(e))
            return ProducerResult(
                topic=topic,
                partition=-1,
                offset=-1,
                timestamp=datetime.now(UTC),
                success=False,
                error=str(e),
            )
    
    def send_batch(
        self,
        topic: str,
        messages: list[dict | BaseModel],
        key: str | None = None,
    ) -> list[ProducerResult]:
        """Отправить пакет сообщений."""
        results = []
        for message in messages:
            result = self.send(topic, message, key)
            results.append(result)
        self.producer.flush()
        return results
    
    def flush(self, timeout: float | None = None) -> None:
        """Flush producer buffer."""
        self.producer.flush(timeout=timeout)
    
    def get_producer_stats(self) -> ProducerStats:
        """Получить статистику producer."""
        return self._producer_stats
    
    # =====================
    # Consumer Operations
    # =====================
    
    def _create_consumer(
        self,
        topics: list[str],
        group_id: str,
        client_id_suffix: str,
        consumer_timeout_ms: int,
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = True,
    ) -> KafkaConsumer:
        """Создать consumer с указанными параметрами."""
        return KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            client_id=f"{self.client_id}_{client_id_suffix}",
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            consumer_timeout_ms=consumer_timeout_ms,
        )
    
    def create_consumer(
        self,
        topics: list[str],
        group_id: str = "test_group",
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = True,
    ) -> KafkaConsumer:
        """Создать consumer для указанных топиков."""
        consumer = self._create_consumer(
            topics=topics,
            group_id=group_id,
            client_id_suffix="consumer",
            consumer_timeout_ms=self.timeout_ms,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
        )
        
        self._consumer = consumer
        self._consumer_stats.topics = topics
        self._consumer_stats.start_time = datetime.now(UTC)
        
        logger.info("Consumer created", topics=topics, group_id=group_id)
        return consumer
    
    def consume_one(
        self,
        topics: list[str],
        group_id: str = "test_group",
        timeout_ms: int | None = None,
    ) -> ConsumedMessage | None:
        """Получить одно сообщение."""
        timeout = timeout_ms or self.timeout_ms
        
        consumer = self._create_consumer(
            topics=topics,
            group_id=group_id,
            client_id_suffix="consumer_once",
            consumer_timeout_ms=timeout,
        )
        
        try:
            for msg in consumer:
                consumed = ConsumedMessage(
                    topic=msg.topic,
                    partition=msg.partition,
                    offset=msg.offset,
                    key=msg.key,
                    value=msg.value,
                    headers=msg.headers,
                    timestamp=datetime.fromtimestamp(msg.timestamp / 1000),
                    timestamp_type=msg.timestamp_type,
                )
                
                self._consumer_stats.messages_consumed += 1
                self._consumer_stats.last_offset = msg.offset
                self._consumer_stats.last_message_time = datetime.now(UTC)
                
                return consumed
        finally:
            consumer.close()
        
        return None
    
    def consume_batch(
        self,
        topics: list[str],
        max_messages: int = 10,
        group_id: str = "test_group",
        timeout_ms: int | None = None,
    ) -> list[ConsumedMessage]:
        """Получить пакет сообщений."""
        timeout = timeout_ms or self.timeout_ms
        messages = []
        
        consumer = self._create_consumer(
            topics=topics,
            group_id=group_id,
            client_id_suffix="consumer_batch",
            consumer_timeout_ms=timeout,
        )
        
        try:
            for msg in consumer:
                consumed = ConsumedMessage(
                    topic=msg.topic,
                    partition=msg.partition,
                    offset=msg.offset,
                    key=msg.key,
                    value=msg.value,
                    headers=msg.headers,
                    timestamp=datetime.fromtimestamp(msg.timestamp / 1000),
                    timestamp_type=msg.timestamp_type,
                )
                messages.append(consumed)
                
                self._consumer_stats.messages_consumed += 1
                self._consumer_stats.last_offset = msg.offset
                self._consumer_stats.last_message_time = datetime.now(UTC)
                
                if len(messages) >= max_messages:
                    break
        finally:
            consumer.close()
        
        return messages
    
    def consume_until(
        self,
        topics: list[str],
        predicate: Callable[[ConsumedMessage], bool],
        group_id: str = "test_group",
        timeout_seconds: float = 30.0,
    ) -> ConsumedMessage | None:
        """Получать сообщения пока predicate не вернёт True."""
        start_time = time.time()
        
        consumer = self._create_consumer(
            topics=topics,
            group_id=group_id,
            client_id_suffix="consumer_until",
            consumer_timeout_ms=1000,
        )
        
        try:
            while time.time() - start_time < timeout_seconds:
                for msg in consumer:
                    consumed = ConsumedMessage(
                        topic=msg.topic,
                        partition=msg.partition,
                        offset=msg.offset,
                        key=msg.key,
                        value=msg.value,
                        headers=msg.headers,
                        timestamp=datetime.fromtimestamp(msg.timestamp / 1000),
                        timestamp_type=msg.timestamp_type,
                    )
                    
                    if predicate(consumed):
                        return consumed
        finally:
            consumer.close()
        
        return None
    
    def get_consumer_stats(self) -> ConsumerStats:
        """Получить статистику consumer."""
        return self._consumer_stats
    
    # =====================
    # Context Managers
    # =====================
    
    @contextmanager
    def producer_context(self) -> Generator[KafkaProducer, None, None]:
        """Context manager для producer."""
        try:
            yield self.producer
        finally:
            self.producer.flush()
    
    @contextmanager
    def consumer_context(
        self,
        topics: list[str],
        group_id: str = "test_group",
    ) -> Generator[KafkaConsumer, None, None]:
        """Context manager для consumer."""
        consumer = self.create_consumer(topics, group_id)
        try:
            yield consumer
        finally:
            consumer.close()
    
    # =====================
    # Cleanup
    # =====================
    
    def close(self) -> None:
        """Закрыть все соединения."""
        if self._producer:
            self._producer.flush()
            self._producer.close()
            self._producer = None
            logger.debug("Producer closed")
        
        if self._consumer:
            self._consumer.close()
            self._consumer = None
            logger.debug("Consumer closed")
        
        if self._admin_client:
            self._admin_client.close()
            self._admin_client = None
            logger.debug("Admin client closed")
        
        logger.info("Kafka client closed")
    
    def __enter__(self) -> "KafkaClient":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()


class KafkaTestHelper:
    """Вспомогательный класс для тестирования Kafka."""
    
    def __init__(self, client: KafkaClient):
        self.client = client
    
    def send_and_receive(
        self,
        topic: str,
        message: dict | BaseModel,
        group_id: str = "test_helper_group",
        timeout_ms: int = 10000,
    ) -> tuple[ProducerResult, ConsumedMessage | None]:
        """Отправить сообщение и получить его обратно."""
        # Отправляем
        send_result = self.client.send(topic, message)
        
        if not send_result.success:
            return send_result, None
        
        # Получаем
        received = self.client.consume_one([topic], group_id, timeout_ms)
        
        return send_result, received
    
    def wait_for_message(
        self,
        topic: str,
        expected_key: str | None = None,
        expected_field: str | None = None,
        expected_value: Any = None,
        timeout_seconds: float = 30.0,
        group_id: str = "test_helper_group",
    ) -> ConsumedMessage | None:
        """Ждать конкретное сообщение."""
        def predicate(msg: ConsumedMessage) -> bool:
            if expected_key and msg.key != expected_key:
                return False
            
            if expected_field and expected_value:
                try:
                    value_dict = msg.value_as_dict()
                    return value_dict.get(expected_field) == expected_value
                except (json.JSONDecodeError, KeyError):
                    return False
            
            return True
        
        return self.client.consume_until(
            [topic],
            predicate,
            group_id,
            timeout_seconds,
        )
    
    def purge_topic(
        self,
        topic: str,
        group_id: str = "purge_group",
        timeout_ms: int = 5000,
    ) -> int:
        """Вычитать все сообщения из топика (для очистки)."""
        messages = self.client.consume_batch(
            [topic],
            max_messages=10000,
            group_id=group_id,
            timeout_ms=timeout_ms,
        )
        return len(messages)
    
    def assert_message_received(
        self,
        topic: str,
        expected_value: dict,
        timeout_ms: int = 10000,
        group_id: str = "assert_group",
    ) -> ConsumedMessage:
        """Assert что сообщение с ожидаемым значением получено."""
        received = self.client.consume_one([topic], group_id, timeout_ms)
        
        if received is None:
            raise AssertionError(f"No message received from topic '{topic}'")
        
        actual_value = received.value_as_dict()
        
        for key, value in expected_value.items():
            if key not in actual_value:
                raise AssertionError(f"Key '{key}' not found in message")
            if actual_value[key] != value:
                raise AssertionError(
                    f"Value mismatch for key '{key}': "
                    f"expected {value}, got {actual_value[key]}"
                )
        
        return received





