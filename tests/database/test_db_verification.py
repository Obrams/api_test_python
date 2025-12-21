"""
Тесты верификации данных через БД.

Паттерн тестирования:
1. Выполняем API вызов
2. Сохраняем данные в БД
3. Проверяем через SQL запросы

Запуск:
    pytest tests/database/ -v
    pytest -m database -v
"""
import pytest
from http import HTTPStatus

from src.clients.rest_client import RestClient
from src.clients.database_client import DatabaseClient
from src.utils.db_assertions import (
    assert_row_exists,
    assert_row_not_exists,
    assert_row_count,
    assert_field_equals,
    assert_user_matches_api,
    assert_post_matches_api,
)


class TestUserDatabaseVerification:
    """Тесты верификации пользователей через БД."""
    
    @pytest.mark.database
    @pytest.mark.smoke
    def test_create_user_and_verify_in_db(
        self,
        rest_client: RestClient,
        db_client: DatabaseClient,
        random_user,
    ):
        """
        Создание пользователя через API и проверка в БД.
        
        1. POST /users - создаём пользователя
        2. Сохраняем в БД
        3. Проверяем через SQL
        """
        # 1. Создаём пользователя через API
        response = rest_client.post("/users", json=random_user.model_dump())
        assert response.status_code == HTTPStatus.CREATED
        
        api_user = response.json()
        
        # 2. Сохраняем в БД
        db_client.save_user(api_user)
        
        # 3. Проверяем через SQL
        db_user = db_client.query_one(
            "SELECT * FROM users WHERE name = :name",
            {"name": random_user.name}
        )
        
        assert db_user is not None, "User not found in database"
        assert db_user["name"] == random_user.name
        assert db_user["email"] == random_user.email
    
    @pytest.mark.database
    def test_get_user_and_save_to_db(
        self,
        rest_client: RestClient,
        db_client: DatabaseClient,
    ):
        """
        Получение пользователя из API и сохранение в БД.
        
        1. GET /users/1 - получаем пользователя
        2. Сохраняем в БД
        3. Проверяем через assert_row_exists
        """
        # 1. Получаем пользователя из API
        response = rest_client.get("/users/1")
        assert response.status_code == HTTPStatus.OK
        
        api_user = response.json()
        
        # 2. Сохраняем в БД
        db_client.save_user(api_user)
        
        # 3. Проверяем через SQL assertions
        assert_row_exists(db_client, "users", {"external_id": api_user["id"]})
        assert_user_matches_api(db_client, api_user)
    
    @pytest.mark.database
    def test_save_multiple_users(
        self,
        rest_client: RestClient,
        db_client: DatabaseClient,
    ):
        """
        Сохранение нескольких пользователей и проверка count.
        
        1. GET /users - получаем всех пользователей
        2. Сохраняем в БД
        3. Проверяем количество через assert_row_count
        """
        # 1. Получаем пользователей из API
        response = rest_client.get("/users")
        assert response.status_code == HTTPStatus.OK
        
        users = response.json()
        
        # 2. Сохраняем в БД
        for user in users:
            db_client.save_user(user)
        
        # 3. Проверяем количество
        assert_row_count(db_client, "users", len(users))
    
    @pytest.mark.database
    def test_verify_user_field(
        self,
        db_client: DatabaseClient,
        db_with_user: dict,
    ):
        """
        Проверка конкретного поля пользователя.
        """
        assert_field_equals(
            db_client,
            "users",
            pk_column="external_id",
            pk_value=db_with_user["id"],
            field="email",
            expected_value=db_with_user["email"],
        )


class TestPostDatabaseVerification:
    """Тесты верификации постов через БД."""
    
    @pytest.mark.database
    @pytest.mark.smoke
    def test_create_post_and_verify_in_db(
        self,
        rest_client: RestClient,
        db_client: DatabaseClient,
        random_post,
    ):
        """
        Создание поста через API и проверка в БД.
        """
        # 1. Создаём пост через API
        response = rest_client.post("/posts", json=random_post.model_dump())
        assert response.status_code == HTTPStatus.CREATED
        
        api_post = response.json()
        
        # 2. Сохраняем в БД
        db_client.save_post(api_post)
        
        # 3. Проверяем через SQL
        db_post = db_client.query_one(
            "SELECT * FROM posts WHERE title = :title",
            {"title": random_post.title}
        )
        
        assert db_post is not None, "Post not found in database"
        assert db_post["title"] == random_post.title
        assert db_post["body"] == random_post.body
    
    @pytest.mark.database
    def test_get_post_and_verify_match(
        self,
        rest_client: RestClient,
        db_client: DatabaseClient,
    ):
        """
        Получение поста и проверка соответствия API и БД.
        """
        # 1. Получаем пост из API
        response = rest_client.get("/posts/1")
        assert response.status_code == HTTPStatus.OK
        
        api_post = response.json()
        
        # 2. Сохраняем в БД
        db_client.save_post(api_post)
        
        # 3. Проверяем соответствие
        assert_post_matches_api(db_client, api_post)


class TestRawSQLQueries:
    """Тесты с использованием raw SQL запросов."""
    
    @pytest.mark.database
    def test_custom_sql_query(
        self,
        db_client: DatabaseClient,
        db_with_user: dict,
    ):
        """
        Выполнение кастомного SQL запроса.
        """
        # Используем raw SQL для сложных запросов
        result = db_client.query_one(
            """
            SELECT 
                name,
                email,
                UPPER(username) as username_upper
            FROM users 
            WHERE external_id = :id
            """,
            {"id": db_with_user["id"]}
        )
        
        assert result is not None
        assert result["name"] == db_with_user["name"]
        assert result["username_upper"] == db_with_user["username"].upper()
    
    @pytest.mark.database
    def test_count_query(
        self,
        db_client: DatabaseClient,
        db_with_user: dict,
    ):
        """
        Подсчёт записей через SQL.
        """
        count = db_client.count("users")
        assert count == 1
        
        # С условием
        count_by_email = db_client.count("users", {"email": db_with_user["email"]})
        assert count_by_email == 1


class TestAPILogging:
    """Тесты логирования API вызовов."""
    
    @pytest.mark.database
    def test_log_api_call(
        self,
        rest_client: RestClient,
        db_client: DatabaseClient,
    ):
        """
        Логирование API вызова в БД.
        """
        import time
        
        # 1. Делаем API вызов
        start = time.time()
        response = rest_client.get("/users/1")
        duration_ms = (time.time() - start) * 1000
        
        # 2. Логируем в БД
        db_client.log_api_call(
            method="GET",
            url="/users/1",
            status_code=response.status_code,
            response_body=response.json(),
            duration_ms=duration_ms,
            test_name="test_log_api_call",
        )
        
        # 3. Проверяем лог
        logs = db_client.get_api_logs(method="GET", url_contains="/users/1")
        assert len(logs) == 1
        assert logs[0]["status_code"] == HTTPStatus.OK
        assert logs[0]["test_name"] == "test_log_api_call"


class TestNegativeCases:
    """Негативные тесты для БД assertions."""
    
    @pytest.mark.database
    @pytest.mark.negative
    def test_assert_row_not_exists(
        self,
        db_client: DatabaseClient,
    ):
        """
        Проверка, что строка НЕ существует.
        """
        # Должно пройти - пользователь не существует
        assert_row_not_exists(
            db_client,
            "users",
            {"email": "nonexistent@example.com"}
        )
    
    @pytest.mark.database
    @pytest.mark.negative
    def test_row_exists_fails_when_not_found(
        self,
        db_client: DatabaseClient,
    ):
        """
        assert_row_exists должен упасть если строка не найдена.
        """
        from src.utils.db_assertions import DatabaseAssertionError
        
        with pytest.raises(DatabaseAssertionError):
            assert_row_exists(
                db_client,
                "users",
                {"email": "nonexistent@example.com"}
            )





