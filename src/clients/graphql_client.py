"""
GraphQL клиент с поддержкой queries, mutations и subscriptions.
"""
from typing import Any, AsyncIterator
from pathlib import Path
import httpx
from gql import gql, Client, GraphQLRequest
from gql.transport.httpx import HTTPXTransport
from gql.transport.websockets import WebsocketsTransport
import structlog

logger = structlog.get_logger(__name__)


class GraphQLClient:
    """GraphQL клиент на базе gql с поддержкой queries, mutations и subscriptions."""
    
    def __init__(
        self,
        endpoint: str,
        ws_endpoint: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        fetch_schema: bool = False,
    ):
        self.endpoint = endpoint
        self.ws_endpoint = ws_endpoint
        self.headers = headers or {}
        self.timeout = timeout
        
        # HTTP транспорт для queries/mutations
        transport = HTTPXTransport(
            url=endpoint,
            headers=self.headers,
            timeout=timeout,
        )
        
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=fetch_schema,
        )
        
        logger.info("GraphQL client initialized", endpoint=endpoint)
    
    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Выполнить GraphQL запрос.
        
        Args:
            query: GraphQL запрос (query или mutation)
            variables: Переменные запроса
            operation_name: Имя операции (для документов с несколькими операциями)
        
        Returns:
            Результат запроса
        """
        logger.debug("Executing GraphQL", operation=operation_name)
        
        request = GraphQLRequest(
            gql(query),
            variable_values=variables,
            operation_name=operation_name,
        )
        result = self.client.execute(request)
        
        logger.debug("GraphQL response received")
        return result
    
    def query(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """Alias для execute - выполнить query."""
        return self.execute(query, variables, operation_name)
    
    def mutate(
        self,
        mutation: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """Выполнить mutation."""
        return self.execute(mutation, variables, operation_name)
    
    async def subscribe(
        self,
        subscription: str,
        variables: dict[str, Any] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Подписка на GraphQL subscription через WebSocket.
        
        Args:
            subscription: GraphQL subscription запрос
            variables: Переменные запроса
        
        Yields:
            Результаты subscription
        """
        if not self.ws_endpoint:
            raise ValueError("WebSocket endpoint not configured for subscriptions")
        
        logger.debug("Starting GraphQL subscription")
        
        transport = WebsocketsTransport(
            url=self.ws_endpoint,
            headers=self.headers,
        )
        
        async with Client(transport=transport) as session:
            request = GraphQLRequest(
                gql(subscription),
                variable_values=variables,
            )
            async for result in session.subscribe(request):
                logger.debug("Subscription message received")
                yield result
    
    def execute_from_file(
        self,
        file_path: str | Path,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Выполнить запрос из файла.
        
        Args:
            file_path: Путь к .graphql файлу
            variables: Переменные запроса
            operation_name: Имя операции
        
        Returns:
            Результат запроса
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"GraphQL file not found: {path}")
        
        query = path.read_text(encoding="utf-8")
        return self.execute(query, variables, operation_name)
    
    def raw_request(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """
        Выполнить raw HTTP запрос (для тестирования ошибок).
        
        Returns:
            Raw httpx.Response объект
        """
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self.endpoint,
                json={
                    "query": query,
                    "variables": variables or {},
                },
                headers={
                    "Content-Type": "application/json",
                    **self.headers,
                },
            )
        return response


class GraphQLClientAsync:
    """Асинхронная версия GraphQL клиента."""
    
    def __init__(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Асинхронное выполнение GraphQL запроса."""
        response = await self.client.post(
            self.endpoint,
            json={
                "query": query,
                "variables": variables or {},
            },
            headers={
                "Content-Type": "application/json",
                **self.headers,
            },
        )
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            logger.warning("GraphQL errors", errors=data["errors"])
        
        return data.get("data", {})
    
    async def aclose(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self) -> "GraphQLClientAsync":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()


