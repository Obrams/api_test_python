"""
Тесты gRPC streaming операций.
"""
import pytest
import allure
from unittest.mock import Mock, MagicMock
import grpc

from src.clients.grpc_client import GrpcClient


@allure.epic("gRPC API")
@allure.feature("Streaming")
class TestServerStreaming:
    """Тесты server streaming."""
    
    @allure.story("Server Streaming")
    @pytest.mark.smoke
    @pytest.mark.streaming
    def test_server_streaming_single_response(self):
        """Server streaming с одним ответом."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.data = "Single response"
        mock_stub_instance.ServerStream.return_value = iter([mock_response])
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        responses = list(client.server_streaming(
            stub_class=mock_stub_class,
            method_name="ServerStream",
            request=Mock()
        ))
        
        assert len(responses) == 1
        assert responses[0].data == "Single response"
    
    @allure.story("Server Streaming")
    @pytest.mark.streaming
    def test_server_streaming_multiple_responses(self):
        """Server streaming с множеством ответов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_responses = [Mock(index=i) for i in range(10)]
        mock_stub_instance.ServerStream.return_value = iter(mock_responses)
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        responses = list(client.server_streaming(
            stub_class=mock_stub_class,
            method_name="ServerStream",
            request=Mock()
        ))
        
        assert len(responses) == 10
        for i, resp in enumerate(responses):
            assert resp.index == i
    
    @allure.story("Server Streaming")
    @pytest.mark.streaming
    def test_server_streaming_empty(self):
        """Server streaming без ответов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_stub_instance.ServerStream.return_value = iter([])
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        responses = list(client.server_streaming(
            stub_class=mock_stub_class,
            method_name="ServerStream",
            request=Mock()
        ))
        
        assert len(responses) == 0
    
    @allure.story("Server Streaming")
    @pytest.mark.negative
    @pytest.mark.streaming
    def test_server_streaming_error_mid_stream(self):
        """Ошибка в середине stream."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        def error_generator():
            yield Mock(data="First")
            yield Mock(data="Second")
            raise grpc.RpcError()
        
        mock_stub_instance.ServerStream.return_value = error_generator()
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        responses = []
        with pytest.raises(grpc.RpcError):
            for resp in client.server_streaming(
                stub_class=mock_stub_class,
                method_name="ServerStream",
                request=Mock()
            ):
                responses.append(resp)
        
        assert len(responses) == 2


@allure.epic("gRPC API")
@allure.feature("Streaming")
class TestClientStreaming:
    """Тесты client streaming."""
    
    @allure.story("Client Streaming")
    @pytest.mark.smoke
    @pytest.mark.streaming
    def test_client_streaming_single_request(self):
        """Client streaming с одним запросом."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.total = 1
        mock_stub_instance.ClientStream.return_value = mock_response
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        requests = [Mock()]
        response = client.client_streaming(
            stub_class=mock_stub_class,
            method_name="ClientStream",
            request_iterator=iter(requests)
        )
        
        assert response.total == 1
    
    @allure.story("Client Streaming")
    @pytest.mark.streaming
    def test_client_streaming_multiple_requests(self):
        """Client streaming с множеством запросов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.total = 10
        mock_stub_instance.ClientStream.return_value = mock_response
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        requests = [Mock() for _ in range(10)]
        response = client.client_streaming(
            stub_class=mock_stub_class,
            method_name="ClientStream",
            request_iterator=iter(requests)
        )
        
        assert response.total == 10
    
    @allure.story("Client Streaming")
    @pytest.mark.streaming
    def test_client_streaming_empty(self):
        """Client streaming без запросов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_response = Mock()
        mock_response.total = 0
        mock_stub_instance.ClientStream.return_value = mock_response
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        response = client.client_streaming(
            stub_class=mock_stub_class,
            method_name="ClientStream",
            request_iterator=iter([])
        )
        
        assert response.total == 0


@allure.epic("gRPC API")
@allure.feature("Streaming")
class TestBidirectionalStreaming:
    """Тесты bidirectional streaming."""
    
    @allure.story("Bidirectional Streaming")
    @pytest.mark.smoke
    @pytest.mark.streaming
    def test_bidirectional_streaming_echo(self):
        """Bidirectional streaming echo."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_responses = [
            Mock(message="Echo 1"),
            Mock(message="Echo 2"),
            Mock(message="Echo 3"),
        ]
        mock_stub_instance.BidiStream.return_value = iter(mock_responses)
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        requests = [Mock() for _ in range(3)]
        responses = list(client.bidirectional_streaming(
            stub_class=mock_stub_class,
            method_name="BidiStream",
            request_iterator=iter(requests)
        ))
        
        assert len(responses) == 3
        assert responses[0].message == "Echo 1"
    
    @allure.story("Bidirectional Streaming")
    @pytest.mark.streaming
    def test_bidirectional_streaming_different_count(self):
        """Bidirectional streaming с разным количеством запросов/ответов."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        # 5 ответов на 3 запроса
        mock_responses = [Mock(index=i) for i in range(5)]
        mock_stub_instance.BidiStream.return_value = iter(mock_responses)
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        requests = [Mock() for _ in range(3)]
        responses = list(client.bidirectional_streaming(
            stub_class=mock_stub_class,
            method_name="BidiStream",
            request_iterator=iter(requests)
        ))
        
        assert len(responses) == 5
    
    @allure.story("Bidirectional Streaming")
    @pytest.mark.streaming
    @pytest.mark.parametrize("request_count,response_count", [
        (1, 1),
        (5, 10),
        (10, 5),
        (100, 100),
    ])
    def test_bidirectional_streaming_various_sizes(self, request_count, response_count):
        """Bidirectional streaming с различными размерами."""
        mock_stub_class = Mock()
        mock_stub_instance = Mock()
        mock_stub_class.return_value = mock_stub_instance
        
        mock_responses = [Mock(index=i) for i in range(response_count)]
        mock_stub_instance.BidiStream.return_value = iter(mock_responses)
        
        client = GrpcClient(host="localhost", port=50051)
        client._channel = Mock()
        
        requests = [Mock() for _ in range(request_count)]
        responses = list(client.bidirectional_streaming(
            stub_class=mock_stub_class,
            method_name="BidiStream",
            request_iterator=iter(requests)
        ))
        
        assert len(responses) == response_count







