"""
Тесты Users для Reqres API.
Reqres API: https://reqres.in/api
"""
import pytest
import allure
from http import HTTPStatus

from config.settings import settings
from src.utils.assertions import (
    assert_status_code,
    assert_contains_keys,
    assert_field_equals,
    assert_list_not_empty,
)
from src.models.user import (
    ReqresSingleUserResponse,
    ReqresUsersListResponse,
    ReqresCreateUserResponse,
)


# Маркер для пропуска тестов если нет API ключа
pytestmark = pytest.mark.skipif(
    not settings.reqres_api_key,
    reason="Reqres API требует x-api-key. Установите REQRES_API_KEY в .env"
)


@allure.epic("REST API")
@allure.feature("Reqres Users")
class TestReqresUsersGet:
    """GET операции Reqres Users."""
    
    @allure.story("Get Users List")
    @pytest.mark.smoke
    def test_get_users_list(self, reqres_client):
        """Получение списка пользователей."""
        response = reqres_client.get("/users")
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        
        assert_contains_keys(data, ["page", "per_page", "total", "data"])
        assert_list_not_empty(data["data"])
    
    @allure.story("Get Users List")
    def test_get_users_validates_with_model(self, reqres_client):
        """Валидация списка пользователей через модель."""
        response = reqres_client.get("/users")
        data = response.json()
        
        validated = ReqresUsersListResponse.model_validate(data)
        assert validated.page == 1
        assert len(validated.data) > 0
    
    @allure.story("Get Users List")
    @pytest.mark.parametrize("page", [1, 2])
    def test_get_users_pagination(self, reqres_client, page):
        """Пагинация списка пользователей."""
        response = reqres_client.get("/users", params={"page": page})
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        assert_field_equals(data, "page", page)
    
    @allure.story("Get Users List")
    @pytest.mark.parametrize("per_page", [1, 3, 6, 12])
    def test_get_users_per_page(self, reqres_client, per_page):
        """Количество пользователей на странице."""
        response = reqres_client.get("/users", params={"per_page": per_page})
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        assert len(data["data"]) <= per_page
    
    @allure.story("Get Single User")
    @pytest.mark.parametrize("user_id", [1, 2, 3, 7, 12])
    def test_get_single_user(self, reqres_client, user_id):
        """Получение одного пользователя."""
        response = reqres_client.get(f"/users/{user_id}")
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        
        assert_contains_keys(data, ["data", "support"])
        assert_field_equals(data["data"], "id", user_id)
    
    @allure.story("Get Single User")
    def test_get_single_user_validates_with_model(self, reqres_client):
        """Валидация одного пользователя через модель."""
        response = reqres_client.get("/users/1")
        data = response.json()
        
        validated = ReqresSingleUserResponse.model_validate(data)
        assert validated.data.id == 1
        assert validated.data.email
    
    @allure.story("Get Single User")
    @pytest.mark.negative
    def test_get_nonexistent_user(self, reqres_client):
        """Запрос несуществующего пользователя."""
        response = reqres_client.get("/users/23")
        assert_status_code(response, HTTPStatus.NOT_FOUND)


@allure.epic("REST API")
@allure.feature("Reqres Users")
class TestReqresUsersCreate:
    """POST операции Reqres Users."""
    
    @allure.story("Create User")
    @pytest.mark.smoke
    def test_create_user(self, reqres_client, reqres_user):
        """Создание пользователя."""
        response = reqres_client.post("/users", json=reqres_user)
        
        assert_status_code(response, HTTPStatus.CREATED)
        data = response.json()
        
        assert_contains_keys(data, ["name", "job", "id", "createdAt"])
        assert data["name"] == reqres_user.name
        assert data["job"] == reqres_user.job
    
    @allure.story("Create User")
    def test_create_user_validates_with_model(self, reqres_client, reqres_user):
        """Валидация созданного пользователя через модель."""
        response = reqres_client.post("/users", json=reqres_user)
        data = response.json()
        
        validated = ReqresCreateUserResponse.model_validate(data)
        assert validated.name == reqres_user.name
        assert validated.id  # ID должен быть непустым
    
    @allure.story("Create User")
    def test_create_user_returns_timestamp(self, reqres_client, reqres_user):
        """Создание пользователя возвращает timestamp."""
        response = reqres_client.post("/users", json=reqres_user)
        data = response.json()
        
        assert "createdAt" in data
        assert "T" in data["createdAt"]


@allure.epic("REST API")
@allure.feature("Reqres Users")
class TestReqresUsersUpdate:
    """PUT/PATCH операции Reqres Users."""
    
    @allure.story("Update User")
    @pytest.mark.smoke
    def test_update_user_put(self, reqres_client):
        """Полное обновление пользователя (PUT)."""
        update_data = {"name": "morpheus", "job": "zion resident"}
        response = reqres_client.put("/users/2", json=update_data)
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        
        assert data["name"] == "morpheus"
        assert data["job"] == "zion resident"
        assert "updatedAt" in data
    
    @allure.story("Update User")
    def test_update_user_patch(self, reqres_client):
        """Частичное обновление пользователя (PATCH)."""
        patch_data = {"name": "morpheus", "job": "leader"}
        response = reqres_client.patch("/users/2", json=patch_data)
        
        assert_status_code(response, HTTPStatus.OK)
        data = response.json()
        
        assert data["job"] == "leader"
        assert "updatedAt" in data


@allure.epic("REST API")
@allure.feature("Reqres Users")
class TestReqresUsersDelete:
    """DELETE операции Reqres Users."""
    
    @allure.story("Delete User")
    @pytest.mark.smoke
    def test_delete_user(self, reqres_client):
        """Удаление пользователя."""
        response = reqres_client.delete("/users/2")
        assert_status_code(response, HTTPStatus.NO_CONTENT)
    
    @allure.story("Delete User")
    @pytest.mark.parametrize("user_id", [1, 5, 12])
    def test_delete_different_users(self, reqres_client, user_id):
        """Удаление разных пользователей."""
        response = reqres_client.delete(f"/users/{user_id}")
        assert_status_code(response, HTTPStatus.NO_CONTENT)


@allure.epic("REST API")
@allure.feature("Reqres Users")
class TestReqresDelayed:
    """Тесты с задержкой ответа."""
    
    @allure.story("Delayed Response")
    @pytest.mark.slow
    def test_delayed_response(self, reqres_client):
        """Запрос с искусственной задержкой."""
        response = reqres_client.get("/users", params={"delay": 2})
        
        assert_status_code(response, HTTPStatus.OK)
        assert response.elapsed.total_seconds() >= 2






