"""
Тесты gRPC status codes.
"""
import pytest
import allure
from unittest.mock import Mock
import grpc

from src.clients.grpc_client import GrpcClient


@allure.epic("gRPC API")
@allure.feature("Status Codes")
class TestGrpcStatusCodes:
    """Тесты различных gRPC status codes."""
    
    @allure.story("OK Status")
    @pytest.mark.smoke
    def test_status_ok(self):
        """Успешный ответ (OK)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.message = "Success"
        mock_stub_instance.Call.return_value = mock_response
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        response = client.unary_call(
            stub_class=mock_stub_class,
            method_name="Call",
            request=Mock()
        )
        
        assert response.message == "Success"
    
    @allure.story("NOT_FOUND Status")
    @pytest.mark.negative
    def test_status_not_found(self):
        """Ресурс не найден (NOT_FOUND)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.NOT_FOUND
        error.details = lambda: "Resource not found"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    
    @allure.story("INVALID_ARGUMENT Status")
    @pytest.mark.negative
    def test_status_invalid_argument(self):
        """Невалидный аргумент (INVALID_ARGUMENT)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.INVALID_ARGUMENT
        error.details = lambda: "Invalid argument provided"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    
    @allure.story("UNAUTHENTICATED Status")
    @pytest.mark.negative
    def test_status_unauthenticated(self):
        """Неаутентифицирован (UNAUTHENTICATED)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.UNAUTHENTICATED
        error.details = lambda: "Authentication required"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    
    @allure.story("PERMISSION_DENIED Status")
    @pytest.mark.negative
    def test_status_permission_denied(self):
        """Доступ запрещён (PERMISSION_DENIED)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.PERMISSION_DENIED
        error.details = lambda: "Permission denied"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED
    
    @allure.story("DEADLINE_EXCEEDED Status")
    @pytest.mark.negative
    def test_status_deadline_exceeded(self):
        """Таймаут (DEADLINE_EXCEEDED)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.DEADLINE_EXCEEDED
        error.details = lambda: "Deadline exceeded"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
    
    @allure.story("UNAVAILABLE Status")
    @pytest.mark.negative
    def test_status_unavailable(self):
        """Сервис недоступен (UNAVAILABLE)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.UNAVAILABLE
        error.details = lambda: "Service unavailable"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE
    
    @allure.story("INTERNAL Status")
    @pytest.mark.negative
    def test_status_internal(self):
        """Внутренняя ошибка (INTERNAL)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.INTERNAL
        error.details = lambda: "Internal server error"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    
    @allure.story("RESOURCE_EXHAUSTED Status")
    @pytest.mark.negative
    def test_status_resource_exhausted(self):
        """Ресурсы исчерпаны (RESOURCE_EXHAUSTED)."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.RESOURCE_EXHAUSTED
        error.details = lambda: "Rate limit exceeded"
        mock_stub_instance.Call.side_effect = error
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        with pytest.raises(grpc.RpcError) as exc_info:
            client.unary_call(
                stub_class=mock_stub_class,
                method_name="Call",
                request=Mock()
            )
        
        assert exc_info.value.code() == grpc.StatusCode.RESOURCE_EXHAUSTED






