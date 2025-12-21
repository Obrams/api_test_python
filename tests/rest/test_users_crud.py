"""
CRUD тесты для Users API.
JSONPlaceholder API: https://jsonplaceholder.typicode.com
"""
import pytest
import allure
from http import HTTPStatus

from src.utils.assertions import (
    assert_status_code,
    assert_contains_keys,
    assert_list_not_empty,
    assert_field_equals,
)
from src.models.user import User


@allure.epic("REST API")
@allure.feature("Users")
class TestUsersGet:
    """GET операции с пользователями."""
    
    @allure.story("Get All Users")
    @pytest.mark.smoke
    def test_get_all_users(self, rest_client, users_endpoint):
        """Получение списка всех пользователей."""
        response = rest_client.get(users_endpoint)
        
        assert_status_code(response, HTTPStatus.OK)
        users = response.json()
        
        assert_list_not_empty(users)
        assert len(users) == 10, "JSONPlaceholder имеет 10 пользователей"
    
    @allure.story("Get All Users")
    def test_get_all_users_response_structure(self, rest_client, users_endpoint):
        """Проверка структуры ответа списка пользователей."""
        response = rest_client.get(users_endpoint)
        users = response.json()
        
        required_keys = ["id", "name", "username", "email"]
        for user in users:
            assert_contains_keys(user, required_keys)
    
    @allure.story("Get User By ID")
    @pytest.mark.parametrize("user_id", [1, 2, 3, 5, 7, 10])
    def test_get_user_by_id(self, rest_client, users_endpoint, user_id):
        """Получение пользователя по ID."""
        response = rest_client.get(f"{users_endpoint}/{user_id}")
        
        assert_status_code(response, HTTPStatus.OK)
        user = response.json()
        assert_field_equals(user, "id", user_id)
    
    @allure.story("Get User By ID")
    def test_get_user_contains_address(self, rest_client, users_endpoint):
        """Проверка наличия адреса у пользователя."""
        response = rest_client.get(f"{users_endpoint}/1")
        user = response.json()
        
        assert "address" in user
        address_keys = ["street", "suite", "city", "zipcode", "geo"]
        assert_contains_keys(user["address"], address_keys)
    
    @allure.story("Get User By ID")
    def test_get_user_contains_company(self, rest_client, users_endpoint):
        """Проверка наличия компании у пользователя."""
        response = rest_client.get(f"{users_endpoint}/1")
        user = response.json()
        
        assert "company" in user
        company_keys = ["name", "catchPhrase", "bs"]
        assert_contains_keys(user["company"], company_keys)
    
    @allure.story("Get User By ID")
    def test_get_user_validates_with_model(self, rest_client, users_endpoint):
        """Валидация ответа через Pydantic модель."""
        response = rest_client.get(f"{users_endpoint}/1")
        user_data = response.json()
        
        user = User.model_validate(user_data)
        assert user.id == 1


@allure.epic("REST API")
@allure.feature("Users")
class TestUsersCreate:
    """POST операции - создание пользователей."""
    
    @allure.story("Create User")
    @pytest.mark.smoke
    def test_create_user(self, rest_client, users_endpoint, random_user):
        """Создание нового пользователя."""
        response = rest_client.post(users_endpoint, json=random_user)
        
        assert_status_code(response, HTTPStatus.CREATED)
        created = response.json()
        
        assert "id" in created
        assert created["name"] == random_user.name
        assert created["email"] == random_user.email
    
    @allure.story("Create User")
    def test_create_user_returns_id(self, rest_client, users_endpoint, random_user):
        """Проверка что при создании возвращается ID."""
        response = rest_client.post(users_endpoint, json=random_user)
        created = response.json()
        
        assert "id" in created
        assert isinstance(created["id"], int)
        assert created["id"] > 0
    
    @allure.story("Create User")
    def test_create_user_with_minimal_data(self, rest_client, users_endpoint):
        """Создание пользователя с минимальными данными."""
        minimal_user = {"name": "Test User", "email": "test@test.com", "username": "testuser"}
        response = rest_client.post(users_endpoint, json=minimal_user)
        
        assert_status_code(response, HTTPStatus.CREATED)
    
    @allure.story("Create User")
    def test_create_user_with_full_data(self, rest_client, users_endpoint, random_user):
        """Создание пользователя с полными данными."""
        full_user = random_user.model_dump()
        full_user.update({
            "address": {
                "street": "Test Street",
                "suite": "Apt 1",
                "city": "Test City",
                "zipcode": "12345",
            },
            "company": {
                "name": "Test Company",
                "catchPhrase": "Testing is fun",
                "bs": "test business",
            }
        })
        
        response = rest_client.post(users_endpoint, json=full_user)
        assert_status_code(response, HTTPStatus.CREATED)


@allure.epic("REST API")
@allure.feature("Users")
class TestUsersUpdate:
    """PUT/PATCH операции - обновление пользователей."""
    
    @allure.story("Update User")
    @pytest.mark.smoke
    def test_update_user_put(self, rest_client, users_endpoint):
        """Полное обновление пользователя (PUT)."""
        update_data = {
            "id": 1,
            "name": "Updated Name",
            "username": "updateduser",
            "email": "updated@test.com",
        }
        response = rest_client.put(f"{users_endpoint}/1", json=update_data)
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated["name"] == "Updated Name"
    
    @allure.story("Update User")
    def test_update_user_patch(self, rest_client, users_endpoint):
        """Частичное обновление пользователя (PATCH)."""
        patch_data = {"name": "Patched Name"}
        response = rest_client.patch(f"{users_endpoint}/1", json=patch_data)
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated["name"] == "Patched Name"
    
    @allure.story("Update User")
    @pytest.mark.parametrize("field,value", [
        ("name", "New Name"),
        ("email", "new@email.com"),
        ("phone", "1-234-567-8900"),
        ("website", "https://newsite.com"),
    ])
    def test_update_user_single_field(self, rest_client, users_endpoint, field, value):
        """Обновление отдельных полей пользователя."""
        response = rest_client.patch(f"{users_endpoint}/1", json={field: value})
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated[field] == value


@allure.epic("REST API")
@allure.feature("Users")
class TestUsersDelete:
    """DELETE операции - удаление пользователей."""
    
    @allure.story("Delete User")
    @pytest.mark.smoke
    def test_delete_user(self, rest_client, users_endpoint):
        """Удаление пользователя."""
        response = rest_client.delete(f"{users_endpoint}/1")
        
        assert_status_code(response, HTTPStatus.OK)
    
    @allure.story("Delete User")
    @pytest.mark.parametrize("user_id", [1, 5, 10])
    def test_delete_different_users(self, rest_client, users_endpoint, user_id):
        """Удаление разных пользователей."""
        response = rest_client.delete(f"{users_endpoint}/{user_id}")
        assert_status_code(response, HTTPStatus.OK)


@allure.epic("REST API")
@allure.feature("Users")
class TestUsersNegative:
    """Негативные тесты для Users API."""
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_get_nonexistent_user(self, rest_client, users_endpoint):
        """Запрос несуществующего пользователя."""
        response = rest_client.get(f"{users_endpoint}/999999")
        
        assert_status_code(response, HTTPStatus.NOT_FOUND)
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    @pytest.mark.parametrize("invalid_id", ["abc", "null", "-1", "0"])
    def test_get_user_invalid_id(self, rest_client, users_endpoint, invalid_id):
        """Запрос пользователя с невалидным ID."""
        response = rest_client.get(f"{users_endpoint}/{invalid_id}")
        
        assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_update_nonexistent_user(self, rest_client, users_endpoint):
        """Обновление несуществующего пользователя."""
        response = rest_client.put(
            f"{users_endpoint}/999999",
            json={"name": "Test"}
        )
        # JSONPlaceholder может вернуть 200 (mock), 404 (not found) или 500 (server error)
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.INTERNAL_SERVER_ERROR]







