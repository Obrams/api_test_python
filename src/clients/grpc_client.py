"""
gRPC клиент с поддержкой unary, streaming и bidirectional вызовов.
"""
from typing import Any, Iterator, Callable, TypeVar
import grpc
from google.protobuf.message import Message
from src.utils.retry import retry
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound=Message)


class GrpcClient:
    """gRPC клиент с поддержкой unary, streaming и bidirectional вызовов."""
    
    def __init__(
        self,
        host: str,
        port: int,
        secure: bool = False,
        credentials: grpc.ChannelCredentials | None = None,
        options: list[tuple[str, Any]] | None = None,
    ):
        self.address = f"{host}:{port}"
        self.secure = secure
        self.credentials = credentials
        self.options = options or [
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 10000),
        ]
        self._channel: grpc.Channel | None = None
        
        logger.info("gRPC client initialized", address=self.address, secure=secure)
    
    @property
    def channel(self) -> grpc.Channel:
        """Lazy initialization канала."""
        if self._channel is None:
            if self.secure:
                creds = self.credentials or grpc.ssl_channel_credentials()
                self._channel = grpc.secure_channel(
                    self.address,
                    creds,
                    options=self.options,
                )
            else:
                self._channel = grpc.insecure_channel(
                    self.address,
                    options=self.options,
                )
            logger.debug("gRPC channel created")
        return self._channel
    
    def get_stub(self, stub_class: type[T]) -> T:
        """Получить stub для сервиса."""
        return stub_class(self.channel)
    
    @retry()
    def unary_call(
        self,
        stub_class: type,
        method_name: str,
        request: Message,
        timeout: float | None = None,
        metadata: list[tuple[str, str]] | None = None,
    ) -> Message:
        """
        Выполнить Unary RPC вызов.
        
        Args:
            stub_class: Класс stub'а сервиса
            method_name: Имя метода
            request: Protobuf request
            timeout: Таймаут в секундах
            metadata: gRPC metadata
        
        Returns:
            Protobuf response
        """
        logger.debug("Unary call", method=method_name)
        
        stub = self.get_stub(stub_class)
        method = getattr(stub, method_name)
        
        response = method(request, timeout=timeout, metadata=metadata)
        
        logger.debug("Unary response received")
        return response
    
    def server_streaming(
        self,
        stub_class: type,
        method_name: str,
        request: Message,
        timeout: float | None = None,
        metadata: list[tuple[str, str]] | None = None,
    ) -> Iterator[Message]:
        """
        Server Streaming RPC.
        
        Args:
            stub_class: Класс stub'а сервиса
            method_name: Имя метода
            request: Protobuf request
        
        Yields:
            Protobuf responses
        """
        logger.debug("Server streaming call", method=method_name)
        
        stub = self.get_stub(stub_class)
        method = getattr(stub, method_name)
        
        for response in method(request, timeout=timeout, metadata=metadata):
            logger.debug("Stream message received")
            yield response
    
    def client_streaming(
        self,
        stub_class: type,
        method_name: str,
        request_iterator: Iterator[Message],
        timeout: float | None = None,
        metadata: list[tuple[str, str]] | None = None,
    ) -> Message:
        """
        Client Streaming RPC.
        
        Args:
            stub_class: Класс stub'а сервиса
            method_name: Имя метода
            request_iterator: Итератор request'ов
        
        Returns:
            Protobuf response
        """
        logger.debug("Client streaming call", method=method_name)
        
        stub = self.get_stub(stub_class)
        method = getattr(stub, method_name)
        
        response = method(request_iterator, timeout=timeout, metadata=metadata)
        
        logger.debug("Client streaming response received")
        return response
    
    def bidirectional_streaming(
        self,
        stub_class: type,
        method_name: str,
        request_iterator: Iterator[Message],
        timeout: float | None = None,
        metadata: list[tuple[str, str]] | None = None,
    ) -> Iterator[Message]:
        """
        Bidirectional Streaming RPC.
        
        Args:
            stub_class: Класс stub'а сервиса
            method_name: Имя метода
            request_iterator: Итератор request'ов
        
        Yields:
            Protobuf responses
        """
        logger.debug("Bidirectional streaming call", method=method_name)
        
        stub = self.get_stub(stub_class)
        method = getattr(stub, method_name)
        
        for response in method(request_iterator, timeout=timeout, metadata=metadata):
            yield response
    
    def check_health(self, timeout: float = 5.0) -> bool:
        """Проверить доступность сервиса."""
        try:
            grpc.channel_ready_future(self.channel).result(timeout=timeout)
            return True
        except grpc.FutureTimeoutError:
            logger.warning("gRPC health check timeout")
            return False
    
    def close(self) -> None:
        """Закрыть канал."""
        if self._channel:
            self._channel.close()
            self._channel = None
            logger.debug("gRPC channel closed")
    
    def __enter__(self) -> "GrpcClient":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()


class GrpcClientAsync:
    """Асинхронная версия gRPC клиента."""
    
    def __init__(
        self,
        host: str,
        port: int,
        secure: bool = False,
        credentials: grpc.ChannelCredentials | None = None,
    ):
        self.address = f"{host}:{port}"
        self.secure = secure
        self.credentials = credentials
        self._channel: grpc.aio.Channel | None = None
    
    @property
    def channel(self) -> grpc.aio.Channel:
        """Lazy initialization асинхронного канала."""
        if self._channel is None:
            if self.secure:
                creds = self.credentials or grpc.ssl_channel_credentials()
                self._channel = grpc.aio.secure_channel(self.address, creds)
            else:
                self._channel = grpc.aio.insecure_channel(self.address)
        return self._channel
    
    async def unary_call(
        self,
        stub_class: type,
        method_name: str,
        request: Message,
        timeout: float | None = None,
    ) -> Message:
        """Асинхронный Unary RPC вызов."""
        stub = stub_class(self.channel)
        method = getattr(stub, method_name)
        return await method(request, timeout=timeout)
    
    async def close(self) -> None:
        """Закрыть асинхронный канал."""
        if self._channel:
            await self._channel.close()
            self._channel = None
    
    async def __aenter__(self) -> "GrpcClientAsync":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()






