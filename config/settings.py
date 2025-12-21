"""
Конфигурация проекта - настройки API endpoints и параметров.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Настройки проекта через Pydantic Settings."""
    
    # REST API Endpoints
    rest_base_url: str = Field(
        default="https://jsonplaceholder.typicode.com",
        description="JSONPlaceholder API"
    )
    reqres_base_url: str = Field(
        default="https://reqres.in/api",
        description="Reqres API с аутентификацией"
    )
    httpbin_base_url: str = Field(
        default="https://httpbin.org",
        description="HTTPBin echo API"
    )
    dummyjson_base_url: str = Field(
        default="https://dummyjson.com",
        description="DummyJSON API"
    )
    
    # GraphQL Endpoints
    graphql_countries_url: str = Field(
        default="https://countries.trevorblades.com/graphql",
        description="Countries GraphQL API"
    )
    graphql_spacex_url: str = Field(
        default="https://spacex-production.up.railway.app/",
        description="SpaceX GraphQL API"
    )
    graphql_rickmorty_url: str = Field(
        default="https://rickandmortyapi.com/graphql",
        description="Rick and Morty GraphQL API"
    )
    
    # gRPC Settings
    grpc_host: str = Field(default="grpcb.in", description="gRPC test server host")
    grpc_port: int = Field(default=9000, description="gRPC test server port")
    grpc_secure: bool = Field(default=False, description="Use TLS for gRPC")
    
    # Auth Credentials (Reqres API)
    test_email: str = Field(default="eve.holt@reqres.in")
    test_password: str = Field(default="cityslicka")
    reqres_api_key: str = Field(default="", description="Reqres API Key (x-api-key)")
    
    # Timeouts
    default_timeout: float = Field(default=60.0, description="Default HTTP timeout")
    async_timeout: float = Field(default=60.0, description="Async operations timeout")
    grpc_timeout: float = Field(default=30.0, description="gRPC timeout")
    
    # Retry Settings
    max_retries: int = Field(default=3, description="Max retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries")
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Reports
    allure_results_dir: str = Field(default="reports/allure-results")
    
    # Database
    database_url: str = Field(
        default="postgresql://tester:testpass@localhost:5433/api_tests",
        description="PostgreSQL connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Echo SQL queries (for debugging)"
    )
    
    # Kafka
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Kafka bootstrap servers"
    )
    kafka_consumer_group_id: str = Field(
        default="api_test_group",
        description="Kafka consumer group ID"
    )
    kafka_auto_offset_reset: str = Field(
        default="earliest",
        description="Kafka auto offset reset policy"
    )
    kafka_timeout_ms: int = Field(
        default=30000,
        description="Kafka operations timeout in milliseconds"
    )
    kafka_default_topic: str = Field(
        default="test_topic",
        description="Default Kafka topic for testing"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Глобальный экземпляр настроек
settings = Settings()


