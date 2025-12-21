# API Testing Framework

Python фреймворк для тестирования REST, GraphQL, gRPC API и Kafka.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![pytest](https://img.shields.io/badge/pytest-8.0+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Содержание

- [Особенности](#особенности)
- [Структура проекта](#структура-проекта)
- [Установка](#установка)
- [PostgreSQL](#postgresql)
- [Запуск тестов](#запуск-тестов)
- [API для тестирования](#api-для-тестирования)
- [Архитектура](#архитектура)
- [Примеры тестов](#примеры-тестов)

## Особенности

- REST API тестирование (httpx, sync/async)
- GraphQL тестирование (queries, mutations, subscriptions)
- gRPC тестирование (unary, streaming, bidirectional)
- Kafka тестирование (producer, consumer, integration)
- Database verification (PostgreSQL + SQLAlchemy)
- 130+ тестов (CRUD, auth, messaging, negative cases)
- Pydantic модели для валидации
- Faker для генерации данных
- Allure отчёты
- Retry механизм
- Параллельный запуск (pytest-xdist)

## Структура проекта

```
api_test_python/
├── pyproject.toml          # Конфигурация проекта и зависимости
├── pytest.ini              # Настройки pytest
├── docker-compose.yml      # PostgreSQL для тестов
├── README.md
│
├── config/                 # Конфигурация
│   ├── __init__.py
│   └── settings.py         # Pydantic Settings
│
├── src/                    # Исходный код
│   ├── clients/            # API клиенты
│   │   ├── rest_client.py
│   │   ├── graphql_client.py
│   │   ├── grpc_client.py
│   │   ├── database_client.py  # PostgreSQL клиент
│   │   └── kafka_client.py     # Kafka Producer/Consumer
│   │
│   ├── database/           # SQLAlchemy модели
│   │   ├── base.py
│   │   └── models.py       # UserDB, PostDB, CommentDB, APILogDB
│   │
│   ├── models/             # Pydantic модели
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── auth.py
│   │   └── kafka.py        # Kafka сообщения
│   │
│   └── utils/              # Утилиты
│       ├── assertions.py   # Кастомные assertions
│       ├── db_assertions.py # SQL assertions
│       ├── data_generator.py
│       └── logger.py
│
├── tests/                  # Тесты
│   ├── conftest.py         # Общие фикстуры
│   │
│   ├── rest/               # REST тесты (~40)
│   │   ├── test_users_crud.py
│   │   ├── test_posts_crud.py
│   │   ├── test_comments.py
│   │   ├── test_auth.py
│   │   └── test_reqres_users.py
│   │
│   ├── graphql/            # GraphQL тесты (~30)
│   │   ├── test_countries.py
│   │   ├── test_rickmorty.py
│   │   └── test_graphql_errors.py
│   │
│   ├── grpc/               # gRPC тесты (~30)
│   │   ├── test_grpc_basic.py
│   │   ├── test_grpc_status_codes.py
│   │   └── test_grpc_streaming.py
│   │
│   ├── database/           # Database verification тесты
│   │   ├── conftest.py
│   │   └── test_db_verification.py
│   │
│   └── kafka/              # Kafka тесты (~20)
│       ├── conftest.py
│       ├── test_kafka_producer.py
│       ├── test_kafka_consumer.py
│       └── test_kafka_integration.py
│
├── proto/                  # Protocol Buffers
│   ├── hello.proto
│   └── user.proto
│
└── graphql/                # GraphQL схемы
    └── queries/
        ├── countries.graphql
        └── rickmorty.graphql
```

## Установка

### Требования

- Python 3.11+
- pip или poetry

### Установка зависимостей

```bash
# Клонировать репозиторий
cd api_test_python

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\activate  # Windows

# Установить зависимости
pip install -e ".[dev]"
```

### Альтернатива с poetry

```bash
poetry install
poetry shell
```

## PostgreSQL

Для запуска Database тестов необходим PostgreSQL.

### Запуск через Docker

```bash
# Запустить PostgreSQL и Kafka
docker-compose up -d

# Проверить статус
docker-compose ps

# Остановить
docker-compose down
```

### Настройки подключения

По умолчанию используется:
- Host: `localhost`
- Port: `5432`
- Database: `api_tests`
- User: `tester`
- Password: `testpass`

Можно переопределить через `.env`:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_ECHO=false

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP_ID=api_test_group
KAFKA_TIMEOUT_MS=30000
```

### Database Client

```python
from src.clients import DatabaseClient

db = DatabaseClient("postgresql://tester:testpass@localhost/api_tests")

# Создать таблицы
db.create_tables()

# Сохранить данные
db.save_user({"name": "John", "email": "john@example.com"})

# SQL запросы
user = db.query_one("SELECT * FROM users WHERE id = :id", {"id": 1})
users = db.query_all("SELECT * FROM users")

# Очистка
db.truncate_all()
db.close()
```

### SQL Assertions

```python
from src.utils.db_assertions import (
    assert_row_exists,
    assert_row_count,
    assert_field_equals,
)

# Проверить что строка существует
assert_row_exists(db, "users", {"email": "john@example.com"})

# Проверить количество строк
assert_row_count(db, "users", 10)

# Проверить значение поля
assert_field_equals(db, "users", "id", 1, "name", "John Doe")
```

## Запуск тестов

### Все тесты

```bash
pytest
```

### Smoke тесты (быстрые)

```bash
pytest -m smoke
```

### По типу API

```bash
# Только REST тесты
pytest -m rest

# Только GraphQL тесты
pytest -m graphql

# Только gRPC тесты
pytest -m grpc

# Только Database тесты (требуется PostgreSQL)
pytest -m database

# Только Kafka тесты (требуется Kafka)
pytest -m kafka
```

### Параллельный запуск

```bash
# Автоопределение количества процессов
pytest -n auto

# Фиксированное количество
pytest -n 4
```

### С Allure отчётом

```bash
# Запуск с сохранением результатов
pytest --alluredir=reports/allure-results

# Открыть отчёт
allure serve reports/allure-results
```

### Дополнительные опции

```bash
# Verbose с коротким traceback
pytest -v --tb=short

# Остановка на первой ошибке
pytest -x

# Перезапуск упавших тестов
pytest --reruns 3 --reruns-delay 1

# Исключить медленные тесты
pytest -m "not slow"

# Только негативные тесты
pytest -m negative
```

## API для тестирования

### REST API

| API | URL | Описание |
|-----|-----|----------|
| JSONPlaceholder | https://jsonplaceholder.typicode.com | Fake REST API |
| Reqres | https://reqres.in/api | REST с аутентификацией |
| HTTPBin | https://httpbin.org | Echo API |
| DummyJSON | https://dummyjson.com | Реалистичные данные |

### GraphQL API

| API | URL | Описание |
|-----|-----|----------|
| Countries | https://countries.trevorblades.com/graphql | Страны, языки |
| SpaceX | https://spacex-production.up.railway.app/ | Запуски SpaceX |
| Rick and Morty | https://rickandmortyapi.com/graphql | Персонажи и эпизоды |

### gRPC

| Сервис | Описание |
|--------|----------|
| grpcb.in | gRPC test server |
| Local mock | Mock тесты |

## Архитектура

### REST Client

```python
from src.clients import RestClient

client = RestClient(base_url="https://api.example.com")

# Синхронные вызовы
response = client.get("/users")
response = client.post("/users", json={"name": "John"})

# Асинхронные вызовы
response = await client.aget("/users")
```

### GraphQL Client

```python
from src.clients import GraphQLClient

client = GraphQLClient(endpoint="https://api.example.com/graphql")

result = client.query("""
    query {
        users {
            id
            name
        }
    }
""")
```

### gRPC Client

```python
from src.clients import GrpcClient

client = GrpcClient(host="localhost", port=50051)

response = client.unary_call(
    stub_class=UserServiceStub,
    method_name="GetUser",
    request=GetUserRequest(id=1)
)
```

### Kafka Client

```python
from src.clients import KafkaClient, KafkaTestHelper
from src.models.kafka import UserEventMessage

# Создаём клиент
client = KafkaClient(bootstrap_servers="localhost:9092")

# Отправляем сообщение
result = client.send("my_topic", {"key": "value"})

# Отправляем Pydantic модель
event = UserEventMessage(user_id=123, action="login")
client.send("user_events", event)

# Получаем сообщение
message = client.consume_one(["my_topic"], group_id="my_group")

# Batch операции
messages = client.consume_batch(["my_topic"], max_messages=10)

# Используем helper для тестов
helper = KafkaTestHelper(client)
send_result, received = helper.send_and_receive("topic", {"data": "test"})

client.close()
```

## Примеры тестов

### REST тест

```python
import pytest
from http import HTTPStatus

@pytest.mark.smoke
@pytest.mark.rest
def test_get_users(rest_client):
    response = rest_client.get("/users")
    
    assert response.status_code == HTTPStatus.OK
    users = response.json()
    assert len(users) > 0
```

### GraphQL тест

```python
@pytest.mark.graphql
def test_get_country(graphql_client):
    query = """
    query GetCountry($code: ID!) {
        country(code: $code) {
            name
            capital
        }
    }
    """
    result = graphql_client.query(query, variables={"code": "US"})
    
    assert result["country"]["name"] == "United States"
```

### gRPC тест

```python
@pytest.mark.grpc
def test_unary_call(grpc_client):
    response = grpc_client.unary_call(
        stub_class=HelloServiceStub,
        method_name="SayHello",
        request=HelloRequest(name="World")
    )
    
    assert "World" in response.message
```

### Database тест

```python
@pytest.mark.database
def test_create_user_verified_in_db(rest_client, db_client, random_user):
    # 1. Создаём пользователя через API
    response = rest_client.post("/users", json=random_user.model_dump())
    assert response.status_code == 201
    
    # 2. Сохраняем в БД
    db_client.save_user(response.json())
    
    # 3. Проверяем через SQL
    db_user = db_client.query_one(
        "SELECT * FROM users WHERE name = :name",
        {"name": random_user.name}
    )
    assert db_user["email"] == random_user.email
```

### Kafka тест

```python
@pytest.mark.kafka
def test_send_and_receive_message(kafka_client, kafka_helper, test_topic):
    # Отправляем сообщение
    message = {"order_id": "12345", "status": "created"}
    result = kafka_client.send(test_topic, message)
    
    assert result.success is True
    assert result.offset >= 0
    
    # Получаем сообщение
    received = kafka_client.consume_one([test_topic], group_id="test_group")
    assert received is not None
    assert received.value_as_dict()["order_id"] == "12345"

@pytest.mark.kafka
def test_pydantic_message(kafka_client, test_topic, user_event_message):
    # Отправляем Pydantic модель
    result = kafka_client.send(test_topic, user_event_message)
    assert result.success
    
    # Проверяем через helper
    received = kafka_client.consume_one([test_topic], group_id="test_group")
    assert received.value_as_dict()["user_id"] == user_event_message.user_id
```

## Количество тестов

| Категория | Количество |
|-----------|------------|
| REST CRUD | ~25 |
| REST Auth | ~10 |
| REST Negative | ~10 |
| GraphQL Queries | ~20 |
| GraphQL Errors | ~10 |
| gRPC Basic | ~15 |
| gRPC Streaming | ~15 |
| Database Verification | ~10 |
| Kafka Producer | ~7 |
| Kafka Consumer | ~7 |
| Kafka Integration | ~6 |
| **Итого** | **~135** |

## Технологии

- **httpx** — современный HTTP клиент
- **gql** — GraphQL клиент
- **grpcio** — gRPC для Python
- **kafka-python** — Kafka Producer/Consumer
- **aiokafka** — асинхронный Kafka клиент
- **sqlalchemy** — ORM для PostgreSQL
- **pytest** — тестовый фреймворк
- **pydantic** — валидация данных
- **faker** — генерация тестовых данных
- **allure** — отчётность
- **structlog** — структурированное логирование

## Лицензия

MIT License





