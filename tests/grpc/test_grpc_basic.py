"""Базовые gRPC тесты."""
import pytest
import allure
from unittest.mock import Mock, MagicMock
from src.clients.grpc_client import GrpcClient


@allure.epic("gRPC API")
@allure.feature("Basic Operations")
class TestGrpcClient:
    """Тесты базовой функциональности gRPC клиента."""
    
    @allure.story("Client Initialization")
    @pytest.mark.smoke
    def test_client_initialization(self):
        """Инициализация gRPC клиента."""
        client = GrpcClient(host="localhost", port=50051)
        
        assert client.address == "localhost:50051"
        assert client.secure is False
        
        client.close()
    
    @allure.story("Client Initialization")
    def test_client_initialization_secure(self):
        """Инициализация secure gRPC клиента."""
        client = GrpcClient(host="localhost", port=50051, secure=True)
        
        assert client.secure is True
        
        client.close()
    
    @allure.story("Client Initialization")
    def test_client_context_manager(self):
        """Использование клиента как context manager."""
        with GrpcClient(host="localhost", port=50051) as client:
            assert client.address == "localhost:50051"
    
    @allure.story("Channel Management")
    def test_lazy_channel_initialization(self):
        """Ленивая инициализация канала."""
        client = GrpcClient(host="localhost", port=50051)
        
        assert client._channel is None
        
        client.close()


@allure.epic("gRPC API")
@allure.feature("Mock Tests")
class TestGrpcMockedCalls:
    """Тесты с mock gRPC вызовами."""
    
    @allure.story("Unary Calls")
    @pytest.mark.smoke
    def test_unary_call_mock(self):
        """Mock unary gRPC вызов."""
        # Создаём mock stub и response
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.message = "Hello, World!"
        mock_stub_instance.SayHello.return_value = mock_response
        
        # Создаём mock request
        mock_request = Mock()
        mock_request.name = "World"
        
        # Создаём клиент с mock channel
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        # Вызываем метод
        response = client.unary_call(
            stub_class=mock_stub_class,
            method_name="SayHello",
            request=mock_request
        )
        
        assert response.message == "Hello, World!"
        mock_stub_class.assert_called_once()
        mock_stub_instance.SayHello.assert_called_once()
    
    @allure.story("Unary Calls")
    @pytest.mark.parametrize("name", ["Alice", "Bob", "Charlie", "Тест", "日本語"])
    def test_unary_call_different_names(self, name):
        """Unary вызов с разными именами."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.message = f"Hello, {name}!"
        mock_stub_instance.SayHello.return_value = mock_response
        
        mock_request = Mock()
        mock_request.name = name
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        response = client.unary_call(
            stub_class=mock_stub_class,
            method_name="SayHello",
            request=mock_request
        )
        
        assert name in response.message
    
    @allure.story("Server Streaming")
    def test_server_streaming_mock(self):
        """Mock server streaming gRPC вызов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        # Создаём итератор mock responses
        mock_responses = [
            Mock(message="Response 1"),
            Mock(message="Response 2"),
            Mock(message="Response 3"),
        ]
        mock_stub_instance.StreamHello.return_value = iter(mock_responses)
        
        mock_request = Mock()
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        responses = list(client.server_streaming(
            stub_class=mock_stub_class,
            method_name="StreamHello",
            request=mock_request
        ))
        
        assert len(responses) == 3
        assert responses[0].message == "Response 1"
        assert responses[2].message == "Response 3"
    
    @allure.story("Client Streaming")
    def test_client_streaming_mock(self):
        """Mock client streaming gRPC вызов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.count = 3
        mock_stub_instance.ClientStream.return_value = mock_response
        
        mock_requests = [Mock(), Mock(), Mock()]
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        response = client.client_streaming(
            stub_class=mock_stub_class,
            method_name="ClientStream",
            request_iterator=iter(mock_requests)
        )
        
        assert response.count == 3
    
    @allure.story("Bidirectional Streaming")
    def test_bidirectional_streaming_mock(self):
        """Mock bidirectional streaming gRPC вызов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_responses = [
            Mock(message="Echo 1"),
            Mock(message="Echo 2"),
        ]
        mock_stub_instance.BidiStream.return_value = iter(mock_responses)
        
        mock_requests = [Mock(), Mock()]
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        responses = list(client.bidirectional_streaming(
            stub_class=mock_stub_class,
            method_name="BidiStream",
            request_iterator=iter(mock_requests)
        ))
        
        assert len(responses) == 2


@allure.epic("gRPC API")
@allure.feature("Error Handling")
class TestGrpcErrors:
    """Тесты обработки ошибок gRPC."""
    
    @allure.story("Timeout")
    @pytest.mark.negative
    def test_health_check_timeout(self):
        """Таймаут health check."""
        client = GrpcClient(host="invalid-host", port=50051)
        
        result = client.check_health(timeout=0.1)
        
        assert result is False
        client.close()
    
    @allure.story("Connection Errors")
    @pytest.mark.negative
    def test_connection_error_handling(self):
        """Обработка ошибок соединения."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        import grpc
        mock_stub_instance.SayHello.side_effect = grpc.RpcError()
        
        mock_request = Mock()
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError):
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="SayHello",
                request=mock_request
            )
    
    @allure.story("Invalid Arguments")
    @pytest.mark.negative
    def test_invalid_method_name(self):
        """Невалидное имя метода."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        del mock_stub_instance.NonExistentMethod
        
        mock_request = Mock()
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(AttributeError):
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="NonExistentMethod",
                request=mock_request
            )


@allure.epic("gRPC API")
@allure.feature("Metadata")
class TestGrpcMetadata:
    """Тесты работы с metadata."""
    
    @allure.story("Request Metadata")
    def test_unary_call_with_metadata(self, grpc_metadata):
        """Unary вызов с metadata."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_stub_instance.SayHello.return_value = mock_response
        
        mock_request = Mock()
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        client.unary_call(
            stub_class=mock_stub_class,
            method_name="SayHello",
            request=mock_request,
            metadata=grpc_metadata
        )
        
        mock_stub_instance.SayHello.assert_called_once()
        call_kwargs = mock_stub_instance.SayHello.call_args
        assert call_kwargs.kwargs.get("metadata") == grpc_metadata
    
    @allure.story("Request Timeout")
    def test_unary_call_with_timeout(self):
        """Unary вызов с таймаутом."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_stub_instance.SayHello.return_value = mock_response
        
        mock_request = Mock()
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        timeout = 30.0
        client.unary_call(
            stub_class=mock_stub_class,
            method_name="SayHello",
            request=mock_request,
            timeout=timeout
        )
        
        call_kwargs = mock_stub_instance.SayHello.call_args
        assert call_kwargs.kwargs.get("timeout") == timeout







