"""Настройка структурированного логирования."""
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
) -> None:
    """
    Настроить структурированное логирование.
    
    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        json_format: Использовать JSON формат для production
    """
    # Общие процессоры
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if json_format:
        # JSON формат для production
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console формат для разработки
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Настройка стандартного logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Получить логгер.
    
    Args:
        name: Имя логгера (обычно __name__)
    
    Returns:
        Structlog bound logger
    """
    return structlog.get_logger(name)


class LogContext:
    """Контекстный менеджер для добавления контекста в логи."""
    
    def __init__(self, **context: Any):
        self.context = context
        self._token = None
    
    def __enter__(self) -> "LogContext":
        self._token = structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, *args: Any) -> None:
        if self._token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_request(
    method: str,
    url: str,
    status_code: int | None = None,
    elapsed: float | None = None,
    **extra: Any,
) -> None:
    """
    Залогировать HTTP запрос.
    
    Args:
        method: HTTP метод
        url: URL запроса
        status_code: Статус код ответа
        elapsed: Время выполнения в секундах
        **extra: Дополнительные поля
    """
    logger = get_logger("http")
    
    log_data = {
        "method": method,
        "url": url,
        **extra,
    }
    
    if status_code is not None:
        log_data["status_code"] = status_code
    
    if elapsed is not None:
        log_data["elapsed_ms"] = round(elapsed * 1000, 2)
    
    if status_code and status_code >= 400:
        logger.warning("HTTP request failed", **log_data)
    else:
        logger.info("HTTP request", **log_data)







