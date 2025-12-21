"""
REST API клиент на базе httpx с поддержкой sync/async операций.
"""
from typing import Any
import httpx
from pydantic import BaseModel
from src.utils.retry import retry
import structlog

logger = structlog.get_logger(__name__)


class RestClient:
    """HTTP клиент с поддержкой sync/async операций, retry и Pydantic моделей."""
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(headers or {}),
        }
        self.auth = auth
        self._client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None
        
        if isinstance(timeout, (int, float)):
            self.timeout = httpx.Timeout(
                connect=10.0,
                read=timeout * 2,
                write=30.0,
                pool=10.0,
            )
        else:
            self.timeout = timeout
        
        logger.info("REST client initialized", base_url=self.base_url)
    
    @property
    def client(self) -> httpx.Client:
        """Lazy initialization синхронного клиента."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers,
                auth=self.auth,
                follow_redirects=True,
            )
        return self._client
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """Lazy initialization асинхронного клиента."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers,
                auth=self.auth,
                follow_redirects=True,
            )
        return self._async_client
    
    def _serialize(self, data: dict | BaseModel | None) -> dict | None:
        """Сериализация данных (поддержка Pydantic моделей)."""
        if data is None:
            return None
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")
        return data
    
    @retry()
    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """GET запрос с автоматическим retry."""
        logger.debug("GET request", endpoint=endpoint, params=params)
        response = self.client.get(endpoint, params=params, headers=headers)
        logger.debug("GET response", status=response.status_code)
        return response
    
    @retry()
    def post(
        self,
        endpoint: str,
        json: dict | BaseModel | None = None,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """POST запрос с автоматическим retry."""
        logger.debug("POST request", endpoint=endpoint)
        response = self.client.post(
            endpoint,
            json=self._serialize(json),
            data=data,
            headers=headers,
        )
        logger.debug("POST response", status=response.status_code)
        return response
    
    @retry()
    def put(
        self,
        endpoint: str,
        json: dict | BaseModel | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """PUT запрос с автоматическим retry."""
        logger.debug("PUT request", endpoint=endpoint)
        response = self.client.put(
            endpoint,
            json=self._serialize(json),
            headers=headers,
        )
        logger.debug("PUT response", status=response.status_code)
        return response
    
    @retry()
    def patch(
        self,
        endpoint: str,
        json: dict | BaseModel | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """PATCH запрос с автоматическим retry."""
        logger.debug("PATCH request", endpoint=endpoint)
        response = self.client.patch(
            endpoint,
            json=self._serialize(json),
            headers=headers,
        )
        logger.debug("PATCH response", status=response.status_code)
        return response
    
    @retry()
    def delete(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """DELETE запрос с автоматическим retry."""
        logger.debug("DELETE request", endpoint=endpoint)
        response = self.client.delete(endpoint, headers=headers)
        logger.debug("DELETE response", status=response.status_code)
        return response
    
    def head(self, endpoint: str) -> httpx.Response:
        """HEAD запрос."""
        return self.client.head(endpoint)
    
    def options(self, endpoint: str) -> httpx.Response:
        """OPTIONS запрос."""
        return self.client.options(endpoint)
    
    @retry()
    async def aget(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Асинхронный GET запрос."""
        logger.debug("Async GET request", endpoint=endpoint, params=params)
        response = await self.async_client.get(endpoint, params=params, headers=headers)
        logger.debug("Async GET response", status=response.status_code)
        return response
    
    @retry()
    async def apost(
        self,
        endpoint: str,
        json: dict | BaseModel | None = None,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Асинхронный POST запрос с автоматическим retry."""
        logger.debug("Async POST request", endpoint=endpoint)
        response = await self.async_client.post(
            endpoint,
            json=self._serialize(json),
            data=data,
            headers=headers,
        )
        logger.debug("Async POST response", status=response.status_code)
        return response
    
    @retry()
    async def aput(
        self,
        endpoint: str,
        json: dict | BaseModel | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Асинхронный PUT запрос с автоматическим retry."""
        response = await self.async_client.put(
            endpoint,
            json=self._serialize(json),
            headers=headers,
        )
        return response
    
    @retry()
    async def apatch(
        self,
        endpoint: str,
        json: dict | BaseModel | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Асинхронный PATCH запрос с автоматическим retry."""
        response = await self.async_client.patch(
            endpoint,
            json=self._serialize(json),
            headers=headers,
        )
        return response
    
    @retry()
    async def adelete(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Асинхронный DELETE запрос с автоматическим retry."""
        response = await self.async_client.delete(endpoint, headers=headers)
        return response
    
    def close(self) -> None:
        """Закрыть синхронный клиент."""
        if self._client:
            self._client.close()
            self._client = None
            logger.debug("REST client closed")
    
    async def aclose(self) -> None:
        """Закрыть асинхронный клиент."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
            logger.debug("Async REST client closed")
    
    def __enter__(self) -> "RestClient":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
    
    async def __aenter__(self) -> "RestClient":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()


