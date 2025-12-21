"""
Pydantic модели для Kafka сообщений.
"""
from typing import Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class MessagePriority(str, Enum):
    """Приоритет сообщения."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(str, Enum):
    """Тип сообщения."""
    EVENT = "event"
    COMMAND = "command"
    NOTIFICATION = "notification"
    LOG = "log"
    METRIC = "metric"


class KafkaMessageBase(BaseModel):
    """Базовая модель Kafka сообщения."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: MessageType = Field(default=MessageType.EVENT)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)


class KafkaMessage(KafkaMessageBase):
    """Полная модель Kafka сообщения."""
    topic: str
    key: str | None = None
    value: dict[str, Any]
    headers: dict[str, str] | None = None
    partition: int | None = None


class UserEventMessage(KafkaMessageBase):
    """Событие пользователя."""
    user_id: int
    action: str
    details: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class OrderEventMessage(KafkaMessageBase):
    """Событие заказа."""
    order_id: str
    user_id: int
    status: str
    total_amount: float
    currency: str = "USD"
    items: list[dict[str, Any]] = Field(default_factory=list)


class NotificationMessage(KafkaMessageBase):
    """Уведомление."""
    recipient_id: int
    channel: str  # email, sms, push
    subject: str
    body: str
    template_id: str | None = None
    variables: dict[str, Any] | None = None


class MetricMessage(KafkaMessageBase):
    """Метрика."""
    metric_name: str
    value: float
    unit: str | None = None
    tags: dict[str, str] = Field(default_factory=dict)
    message_type: MessageType = Field(default=MessageType.METRIC)


class LogMessage(KafkaMessageBase):
    """Лог сообщение."""
    level: str  # debug, info, warning, error, critical
    logger_name: str
    message: str
    context: dict[str, Any] | None = None
    exception: str | None = None
    stack_trace: str | None = None
    message_type: MessageType = Field(default=MessageType.LOG)


class CommandMessage(KafkaMessageBase):
    """Команда."""
    command_name: str
    payload: dict[str, Any]
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reply_to: str | None = None
    message_type: MessageType = Field(default=MessageType.COMMAND)


class ProducerResult(BaseModel):
    """Результат отправки сообщения."""
    topic: str
    partition: int
    offset: int
    timestamp: datetime
    success: bool = True
    error: str | None = None


class ConsumedMessage(BaseModel):
    """Полученное сообщение."""
    topic: str
    partition: int
    offset: int
    key: str | None
    value: Any
    headers: list[tuple[str, bytes]] | None
    timestamp: datetime
    timestamp_type: int
    
    def value_as_str(self) -> str:
        """Получить значение как строку."""
        if isinstance(self.value, str):
            return self.value
        if isinstance(self.value, dict):
            import json
            return json.dumps(self.value)
        return str(self.value)
    
    def value_as_dict(self) -> dict[str, Any]:
        """Получить значение как dict."""
        if isinstance(self.value, dict):
            return self.value
        import json
        if isinstance(self.value, str):
            return json.loads(self.value)
        raise ValueError(f"Cannot convert value to dict: {type(self.value)}")


class ConsumerStats(BaseModel):
    """Статистика consumer."""
    messages_consumed: int = 0
    last_offset: int = -1
    topics: list[str] = Field(default_factory=list)
    partitions: dict[str, list[int]] = Field(default_factory=dict)
    start_time: datetime | None = None
    last_message_time: datetime | None = None


class ProducerStats(BaseModel):
    """Статистика producer."""
    messages_sent: int = 0
    messages_failed: int = 0
    topics: list[str] = Field(default_factory=list)
    last_send_time: datetime | None = None


class BatchMessage(BaseModel):
    """Пакет сообщений для batch отправки."""
    topic: str
    messages: list[dict[str, Any]]
    key: str | None = None
    
    def message_count(self) -> int:
        """Количество сообщений в пакете."""
        return len(self.messages)






