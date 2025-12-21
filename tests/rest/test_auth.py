"""
Тесты аутентификации.
Reqres API: https://reqres.in/api
"""
import pytest
import allure
from http import HTTPStatus

from config.settings import settings
from src.utils.assertions import (
    assert_status_code,
    assert_contains_keys,
    assert_error_response,
)
from src.models.auth import LoginRequest, RegisterRequest


# Маркер для пропуска тестов если нет API ключа
pytestmark = pytest.mark.skipif(
    not settings.reqres_api_key,
    reason="Reqres API требует x-api-key. Установите REQRES_API_KEY в .env"
)


@allure.epic("REST API")
@allure.feature("Authentication")
class TestLogin:
    """Тесты логина."""
    
    @allure.story("Login")
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_login_successful(self, reqres_client, auth_credentials):
        """Успешный логин."""
        response = reqres_client.post("/login", json=auth_credentials)
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        assert_contains_keys(data, ["token"])
    
    @allure.story("Login")
    @pytest.mark.auth
    def test_login_returns_token(self, reqres_client, auth_credentials):
        """Логин возвращает токен."""
        response = reqres_client.post("/login", json=auth_credentials)
        data = response.json()
        
        assert "token" in data
        assert len(data["token"]) > 0
        assert isinstance(data["token"], str)
    
    @allure.story("Login")
    @pytest.mark.auth
    def test_login_with_pydantic_model(self, reqres_client):
        """Логин через Pydantic модель."""
        login_request = LoginRequest(
            email="eve.holt@reqres.in",
            password="cityslicka"
        )
        response = reqres_client.post("/login", json=login_request)
        
        assert_status_code(response, HTTPStatus.OK)
    
    @allure.story("Login")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_login_missing_password(self, reqres_client):
        """Логин без пароля."""
        response = reqres_client.post("/login", json={"email": "test@test.com"})
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)
    
    @allure.story("Login")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_login_missing_email(self, reqres_client):
        """Логин без email."""
        response = reqres_client.post("/login", json={"password": "password"})
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)
    
    @allure.story("Login")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_login_empty_body(self, reqres_client):
        """Логин с пустым телом запроса."""
        response = reqres_client.post("/login", json={})
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)
    
    @allure.story("Login")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_login_invalid_credentials(self, reqres_client, invalid_credentials):
        """Логин с неверными credentials."""
        response = reqres_client.post("/login", json=invalid_credentials)
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)


@allure.epic("REST API")
@allure.feature("Authentication")
class TestRegister:
    """Тесты регистрации."""
    
    @allure.story("Register")
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_register_successful(self, reqres_client):
        """Успешная регистрация."""
        register_data = {
            "email": "eve.holt@reqres.in",
            "password": "pistol"
        }
        response = reqres_client.post("/register", json=register_data)
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        assert_contains_keys(data, ["id", "token"])
    
    @allure.story("Register")
    @pytest.mark.auth
    def test_register_returns_id_and_token(self, reqres_client):
        """Регистрация возвращает ID и токен."""
        register_data = {
            "email": "eve.holt@reqres.in",
            "password": "pistol"
        }
        response = reqres_client.post("/register", json=register_data)
        data = response.json()
        
        assert "id" in data
        assert "token" in data
        assert isinstance(data["id"], int)
        assert isinstance(data["token"], str)
    
    @allure.story("Register")
    @pytest.mark.auth
    def test_register_with_pydantic_model(self, reqres_client):
        """Регистрация через Pydantic модель."""
        register_request = RegisterRequest(
            email="eve.holt@reqres.in",
            password="pistol"
        )
        response = reqres_client.post("/register", json=register_request)
        
        assert_status_code(response, HTTPStatus.OK)
    
    @allure.story("Register")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_register_missing_password(self, reqres_client):
        """Регистрация без пароля."""
        response = reqres_client.post("/register", json={"email": "test@test.com"})
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)
    
    @allure.story("Register")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_register_missing_email(self, reqres_client):
        """Регистрация без email."""
        response = reqres_client.post("/register", json={"password": "password"})
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)
    
    @allure.story("Register")
    @pytest.mark.negative
    @pytest.mark.auth
    def test_register_undefined_user(self, reqres_client, data_generator):
        """Регистрация неопределённого пользователя."""
        register_data = {
            "email": data_generator.email(),
            "password": "password123"
        }
        response = reqres_client.post("/register", json=register_data)
        
        assert_error_response(response, HTTPStatus.BAD_REQUEST)






