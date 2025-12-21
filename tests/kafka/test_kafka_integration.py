"""
Интеграционные тесты Kafka.

Комплексные сценарии взаимодействия с Kafka.
"""
import pytest
import uuid
import time
import allure

from src.clients.kafka_client import KafkaClient, KafkaTestHelper
from src.models.kafka import (
    UserEventMessage,
    OrderEventMessage,
    NotificationMessage,
    CommandMessage,
    LogMessage,
    MessageType,
    MessagePriority,
)


pytestmark = pytest.mark.kafka


@allure.epic("Kafka")
@allure.feature("Integration")
class TestKafkaIntegration:
    """Интеграционные тесты Kafka."""
    
    @allure.story("End-to-End")
    @allure.title("Полный цикл: отправка и получение")
    @pytest.mark.smoke
    def test_send_and_receive_e2e(
        self,
        kafka_helper: KafkaTestHelper,
        test_topic: str,
        sample_message: dict,
    ):
        """E2E тест: отправка и получение сообщения."""
        unique_group = f"e2e_test_{uuid.uuid4().hex[:8]}"
        
        send_result, received = kafka_helper.send_and_receive(
            test_topic,
            sample_message,
            group_id=unique_group,
            timeout_ms=10000,
        )
        
        assert send_result.success
        assert received is not None
        
        received_value = received.value_as_dict()
        assert received_value["id"] == sample_message["id"]
    
    @allure.story("End-to-End")
    @allure.title("Ожидание конкретного сообщения")
    def test_wait_for_specific_message(
        self,
        kafka_client: KafkaClient,
        kafka_helper: KafkaTestHelper,
        test_topic: str,
    ):
        """Тест ожидания конкретного сообщения по полю."""
        unique_group = f"wait_test_{uuid.uuid4().hex[:8]}"
        target_order_id = str(uuid.uuid4())
        
        # Отправляем несколько сообщений
        kafka_client.send(test_topic, {"order_id": "other_1", "status": "pending"})
        kafka_client.send(test_topic, {"order_id": "other_2", "status": "pending"})
        kafka_client.send(test_topic, {"order_id": target_order_id, "status": "completed"})
        
        # Ждём конкретное сообщение
        result = kafka_helper.wait_for_message(
            test_topic,
            expected_field="order_id",
            expected_value=target_order_id,
            timeout_seconds=15.0,
            group_id=unique_group,
        )
        
        assert result is not None
        assert result.value_as_dict()["order_id"] == target_order_id
        assert result.value_as_dict()["status"] == "completed"
    
    @allure.story("Admin операции")
    @allure.title("Управление топиками")
    def test_topic_management(self, kafka_client: KafkaClient):
        """Тест создания, проверки и удаления топика."""
        topic_name = f"test_management_{uuid.uuid4().hex[:8]}"
        
        # Создаём топик
        created = kafka_client.create_topic(topic_name, num_partitions=2)
        assert created is True
        
        # Проверяем существование
        time.sleep(1)  # Даём время на создание
        exists = kafka_client.topic_exists(topic_name)
        assert exists is True
        
        # Удаляем топик
        deleted = kafka_client.delete_topic(topic_name)
        assert deleted is True
    
    @allure.story("Бизнес сценарии")
    @allure.title("Обработка события пользователя")
    def test_user_event_flow(
        self,
        kafka_client: KafkaClient,
        test_topic: str,
        user_event_message: UserEventMessage,
    ):
        """Тест потока события пользователя."""
        unique_group = f"user_event_{uuid.uuid4().hex[:8]}"
        
        # Отправляем событие
        result = kafka_client.send(
            test_topic,
            user_event_message,
            key=str(user_event_message.user_id),
        )
        assert result.success
        
        # Получаем и проверяем
        received = kafka_client.consume_one([test_topic], group_id=unique_group)
        assert received is not None
        
        value = received.value_as_dict()
        assert value["user_id"] == user_event_message.user_id
        assert value["action"] == user_event_message.action
        assert value["message_type"] == MessageType.EVENT.value
    
    @allure.story("Бизнес сценарии")
    @allure.title("Обработка заказа через несколько топиков")
    def test_order_processing_flow(
        self,
        kafka_client: KafkaClient,
        order_event_message: OrderEventMessage,
    ):
        """Тест потока обработки заказа через разные топики."""
        orders_topic = f"orders_{uuid.uuid4().hex[:8]}"
        notifications_topic = f"notifications_{uuid.uuid4().hex[:8]}"
        unique_group = f"order_flow_{uuid.uuid4().hex[:8]}"
        
        # Создаём топики
        kafka_client.create_topic(orders_topic)
        kafka_client.create_topic(notifications_topic)
        
        try:
            # 1. Отправляем заказ
            order_result = kafka_client.send(
                orders_topic,
                order_event_message,
                key=order_event_message.order_id,
            )
            assert order_result.success
            
            # 2. Создаём уведомление о заказе
            notification = NotificationMessage(
                recipient_id=order_event_message.user_id,
                channel="email",
                subject=f"Order {order_event_message.order_id} confirmed",
                body=f"Your order for ${order_event_message.total_amount} has been confirmed.",
            )
            
            notif_result = kafka_client.send(notifications_topic, notification)
            assert notif_result.success
            
            # 3. Проверяем оба сообщения
            order_msg = kafka_client.consume_one([orders_topic], group_id=unique_group)
            notif_msg = kafka_client.consume_one([notifications_topic], group_id=unique_group)
            
            assert order_msg is not None
            assert notif_msg is not None
            
            assert order_msg.value_as_dict()["order_id"] == order_event_message.order_id
            assert notif_msg.value_as_dict()["recipient_id"] == order_event_message.user_id
            
        finally:
            kafka_client.delete_topic(orders_topic)
            kafka_client.delete_topic(notifications_topic)
    
    @allure.story("Assertions")
    @allure.title("Assert получения сообщения с ожидаемым значением")
    def test_assert_message_received(
        self,
        kafka_helper: KafkaTestHelper,
        kafka_client: KafkaClient,
        test_topic: str,
    ):
        """Тест assertion helper для проверки сообщения."""
        unique_group = f"assert_test_{uuid.uuid4().hex[:8]}"
        
        expected_data = {
            "transaction_id": str(uuid.uuid4()),
            "status": "success",
            "amount": 100.50,
        }
        
        kafka_client.send(test_topic, expected_data)
        
        # Используем helper для assertion
        received = kafka_helper.assert_message_received(
            test_topic,
            expected_value={"status": "success"},
            group_id=unique_group,
            timeout_ms=10000,
        )
        
        assert received.value_as_dict()["transaction_id"] == expected_data["transaction_id"]






