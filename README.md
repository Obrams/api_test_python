# API Testing Framework

API testing framework in Python: REST, GraphQL, gRPC, Kafka, PostgreSQL, pytest, Allure.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![pytest](https://img.shields.io/badge/pytest-8.0+-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![CI](https://github.com/Obrams/api_test_python/actions/workflows/ci.yml/badge.svg)

**Topics:** `api-testing` `pytest` `grpc` `kafka` `graphql` `sqlalchemy` `allure`

## Contents

- [Features](#features)
- [Project structure](#project-structure)
- [Installation](#installation)
- [PostgreSQL](#postgresql)
- [Running tests](#running-tests)
- [APIs under test](#apis-under-test)
- [Architecture](#architecture)
- [Test examples](#test-examples)

## Features

- REST API testing (httpx, sync/async)
- GraphQL testing (queries, mutations, subscriptions)
- gRPC testing (unary, streaming, bidirectional)
- Kafka testing (producer, consumer, integration)
- Database verification (PostgreSQL + SQLAlchemy)
- 130+ tests (CRUD, auth, messaging, negative cases)
- Pydantic models for validation
- Faker for test data generation
- Allure reports
- Retry mechanism
- Parallel runs (pytest-xdist)

## Project structure

```
api_test_python/
├── pyproject.toml          # Project configuration and dependencies
├── pytest.ini              # pytest settings
├── docker-compose.yml      # PostgreSQL for tests
├── README.md
│
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py         # Pydantic Settings
│
├── src/                    # Source code
│   ├── clients/            # API clients
│   │   ├── rest_client.py
│   │   ├── graphql_client.py
│   │   ├── grpc_client.py
│   │   ├── database_client.py  # PostgreSQL client
│   │   └── kafka_client.py     # Kafka Producer/Consumer
│   │
│   ├── database/           # SQLAlchemy models
│   │   ├── base.py
│   │   └── models.py       # UserDB, PostDB, CommentDB, APILogDB
│   │
│   ├── models/             # Pydantic models
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── auth.py
│   │   └── kafka.py        # Kafka messages
│   │
│   └── utils/              # Utilities
│       ├── assertions.py   # Custom assertions
│       ├── db_assertions.py # SQL assertions
│       ├── data_generator.py
│       └── logger.py
│
├── tests/                  # Tests
│   ├── conftest.py         # Shared fixtures
│   │
│   ├── rest/               # REST tests (~40)
│   │   ├── test_users_crud.py
│   │   ├── test_posts_crud.py
│   │   ├── test_comments.py
│   │   ├── test_auth.py
│   │   └── test_reqres_users.py
│   │
│   ├── graphql/            # GraphQL tests (~30)
│   │   ├── test_countries.py
│   │   ├── test_rickmorty.py
│   │   └── test_graphql_errors.py
│   │
│   ├── grpc/               # gRPC tests (~30)
│   │   ├── test_grpc_basic.py
│   │   ├── test_grpc_status_codes.py
│   │   └── test_grpc_streaming.py
│   │
│   ├── database/           # Database verification tests
│   │   ├── conftest.py
│   │   └── test_db_verification.py
│   │
│   └── kafka/              # Kafka tests (~20)
│       ├── conftest.py
│       ├── test_kafka_producer.py
│       ├── test_kafka_consumer.py
│       └── test_kafka_integration.py
│
├── proto/                  # Protocol Buffers
│   ├── hello.proto
│   └── user.proto
│
└── graphql/                # GraphQL schemas
    └── queries/
        ├── countries.graphql
        └── rickmorty.graphql
```

## Installation

### Requirements

- Python 3.11+
- pip or poetry

### Install dependencies

```bash
# Clone the repository
cd api_test_python

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"
```

### Alternative: poetry

```bash
poetry install
poetry shell
```

## PostgreSQL

Database tests require PostgreSQL.

### Run via Docker

```bash
# Start PostgreSQL and Kafka
docker-compose up -d

# Check status
docker-compose ps

# Stop
docker-compose down
```

### Connection settings

Defaults:
- Host: `localhost`
- Port: `5432`
- Database: `api_tests`
- User: `tester`
- Password: `testpass`

Can be overridden via `.env`:

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

# Create tables
db.create_tables()

# Save data
db.save_user({"name": "John", "email": "john@example.com"})

# SQL queries
user = db.query_one("SELECT * FROM users WHERE id = :id", {"id": 1})
users = db.query_all("SELECT * FROM users")

# Cleanup
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

# Check that the row exists
assert_row_exists(db, "users", {"email": "john@example.com"})

# Check the row count
assert_row_count(db, "users", 10)

# Check a field value
assert_field_equals(db, "users", "id", 1, "name", "John Doe")
```

## Running tests

### All tests

```bash
pytest
```

### Smoke tests (fast)

```bash
pytest -m smoke
```

### By API type

```bash
# REST tests only
pytest -m rest

# GraphQL tests only
pytest -m graphql

# gRPC tests only
pytest -m grpc

# Database tests only (requires PostgreSQL)
pytest -m database

# Kafka tests only (requires Kafka)
pytest -m kafka
```

### Parallel run

```bash
# Auto-detect the number of workers
pytest -n auto

# Fixed number of workers
pytest -n 4
```

### With Allure report

```bash
# Run and save results
pytest --alluredir=reports/allure-results

# Open the report
allure serve reports/allure-results
```

### Additional options

```bash
# Verbose with short traceback
pytest -v --tb=short

# Stop on first failure
pytest -x

# Rerun failed tests
pytest --reruns 3 --reruns-delay 1

# Exclude slow tests
pytest -m "not slow"

# Negative tests only
pytest -m negative
```

## CI and reports

### GitHub Actions

CI automatically runs REST, GraphQL and gRPC tests on every push and pull request.

**CI status:** [![CI](https://github.com/Obrams/api_test_python/actions/workflows/ci.yml/badge.svg)](https://github.com/Obrams/api_test_python/actions/workflows/ci.yml)

### Allure reports

- **Artifacts:** Allure results and reports are available in [Actions artifacts](https://github.com/Obrams/api_test_python/actions) after every CI run
- **GitHub Pages:** a static Allure report is published to [GitHub Pages](https://obrams.github.io/api_test_python/) (main/master branch only)

To download artifacts:
1. Go to [Actions](https://github.com/Obrams/api_test_python/actions)
2. Select the workflow run
3. Download the artifacts `allure-results-*` or `allure-report-*`
4. To view the report locally: `allure serve <path-to-allure-results>`

## APIs under test

### REST API

| API | URL | Description |
|-----|-----|----------|
| JSONPlaceholder | https://jsonplaceholder.typicode.com | Fake REST API |
| Reqres | https://reqres.in/api | REST with authentication |
| HTTPBin | https://httpbin.org | Echo API |
| DummyJSON | https://dummyjson.com | Realistic data |

### GraphQL API

| API | URL | Description |
|-----|-----|----------|
| Countries | https://countries.trevorblades.com/graphql | Countries, languages |
| SpaceX | https://spacex-production.up.railway.app/ | SpaceX launches |
| Rick and Morty | https://rickandmortyapi.com/graphql | Characters and episodes |

### gRPC

| Service | Description |
|--------|----------|
| grpcb.in | gRPC test server |
| Local mock | Mock tests |

## Architecture

### REST Client

```python
from src.clients import RestClient

client = RestClient(base_url="https://api.example.com")

# Synchronous calls
response = client.get("/users")
response = client.post("/users", json={"name": "John"})

# Asynchronous calls
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

# Create a client
client = KafkaClient(bootstrap_servers="localhost:9092")

# Send a message
result = client.send("my_topic", {"key": "value"})

# Send a Pydantic model
event = UserEventMessage(user_id=123, action="login")
client.send("user_events", event)

# Receive a message
message = client.consume_one(["my_topic"], group_id="my_group")

# Batch operations
messages = client.consume_batch(["my_topic"], max_messages=10)

# Use the test helper
helper = KafkaTestHelper(client)
send_result, received = helper.send_and_receive("topic", {"data": "test"})

client.close()
```

## Design/Architecture

The project demonstrates not only writing tests but also building a shared infrastructure layer for different integration types. Each client solves the specific problems of its domain and exposes a uniform interface to the tests.

### RestClient

**Sync/async support:** a single class with lazy initialization of the synchronous (`httpx.Client`) and asynchronous (`httpx.AsyncClient`) clients. `get/post/put/delete` methods for sync, `aget/apost/aput/adelete` for async. Both clients are created only on first access via `@property`.

**Retry mechanism:** all HTTP methods are wrapped with a `@retry()` decorator with exponential backoff. Configured via `config.settings` (number of attempts, min/max delay). Network errors and transient failures are handled automatically.

**Logging hooks:** structured logging via `structlog` for every request/response — endpoint, parameters and status codes. Pydantic models are supported via `_serialize()` with automatic JSON conversion.

### GraphQLClient

**Schemas and queries:** schema loading via `fetch_schema_from_transport`. Queries can be executed from files via `execute_from_file()` to reuse `.graphql` files. `query()` and `mutate()` are semantic wrappers over `execute()`. Subscriptions are supported via WebSocket transport.

**Error handling strategy:** GraphQL is special — errors can come in the `errors` array with HTTP 200. The client logs warnings but does not raise exceptions (unlike HTTP errors). `raw_request()` is used for negative scenarios — it returns `httpx.Response` so status codes and response bodies can be checked.

### GrpcClient

**A single helper around stubs and methods:** an abstraction over low-level gRPC stubs. `unary_call()`, `server_streaming()`, `client_streaming()` and `bidirectional_streaming()` take `stub_class` and `method_name` as parameters — no need to create stubs manually. Lazy channel initialization via `@property channel` with secure/insecure connection support.

**Streaming:** all streaming types (server, client, bidirectional) are implemented with generators. `server_streaming()` and `bidirectional_streaming()` return `Iterator[Message]`, `client_streaming()` takes `Iterator[Message]` as input. Metadata and timeouts are handled uniformly for all call types.

### KafkaClient + KafkaTestHelper

**Solving "wait for a message":** `consume_until()` with a predicate consumes messages until the condition is met or the timeout expires. `KafkaTestHelper.wait_for_message()` is a high-level wrapper that waits for a message by key or field value. This avoids message-ordering issues and race conditions.

**Test stability:** every consumer gets a unique `group_id` (via UUID fixtures), isolating tests from each other. `consume_one()` and `consume_batch()` create temporary consumers and close them automatically — no connection leaks. `send_and_receive()` in the helper is an atomic send-and-receive operation for E2E tests. `auto_offset_reset="earliest"` is supported to read all messages in a topic.

## Test examples

### REST test

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

### GraphQL test

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

### gRPC test

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

### Database test

```python
@pytest.mark.database
def test_create_user_verified_in_db(rest_client, db_client, random_user):
    # 1. Create a user via the API
    response = rest_client.post("/users", json=random_user.model_dump())
    assert response.status_code == 201
    
    # 2. Save to the DB
    db_client.save_user(response.json())
    
    # 3. Verify via SQL
    db_user = db_client.query_one(
        "SELECT * FROM users WHERE name = :name",
        {"name": random_user.name}
    )
    assert db_user["email"] == random_user.email
```

### Kafka test

```python
@pytest.mark.kafka
def test_send_and_receive_message(kafka_client, kafka_helper, test_topic):
    # Send a message
    message = {"order_id": "12345", "status": "created"}
    result = kafka_client.send(test_topic, message)
    
    assert result.success is True
    assert result.offset >= 0
    
    # Receive a message
    received = kafka_client.consume_one([test_topic], group_id="test_group")
    assert received is not None
    assert received.value_as_dict()["order_id"] == "12345"

@pytest.mark.kafka
def test_pydantic_message(kafka_client, test_topic, user_event_message):
    # Send a Pydantic model
    result = kafka_client.send(test_topic, user_event_message)
    assert result.success
    
    # Verify via the helper
    received = kafka_client.consume_one([test_topic], group_id="test_group")
    assert received.value_as_dict()["user_id"] == user_event_message.user_id
```

## Test count

| Category | Count |
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
| **Total** | **~135** |

## Technologies

- **httpx** — modern HTTP client
- **gql** — GraphQL client
- **grpcio** — gRPC for Python
- **kafka-python** — Kafka Producer/Consumer
- **aiokafka** — async Kafka client
- **sqlalchemy** — ORM for PostgreSQL
- **pytest** — test framework
- **pydantic** — data validation
- **faker** — test data generation
- **allure** — reporting
- **structlog** — structured logging

## Case study

### Problems

Typical problems the project solves: scattered API tests without a shared client, no DB verification, no stable Kafka/gRPC testing, no single report.

### Solutions

Solutions: shared clients for all protocols, Pydantic models, SQLAlchemy + SQL assertions, Kafka helper, CI + Allure.

## License

MIT License





