"""
Тесты для Comments API.
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


@allure.epic("REST API")
@allure.feature("Comments")
class TestCommentsGet:
    """GET операции с комментариями."""
    
    @allure.story("Get All Comments")
    @pytest.mark.smoke
    def test_get_all_comments(self, rest_client, comments_endpoint):
        """Получение списка всех комментариев."""
        response = rest_client.get(comments_endpoint)
        
        assert_status_code(response, HTTPStatus.OK)
        comments = response.json()
        
        assert_list_not_empty(comments)
        assert len(comments) == 500, "JSONPlaceholder имеет 500 комментариев"
    
    @allure.story("Get All Comments")
    def test_get_comments_structure(self, rest_client, comments_endpoint):
        """Проверка структуры ответа комментариев."""
        response = rest_client.get(comments_endpoint, params={"postId": 1})
        comments = response.json()
        
        required_keys = ["id", "postId", "name", "email", "body"]
        for comment in comments:
            assert_contains_keys(comment, required_keys)
    
    @allure.story("Get Comment By ID")
    @pytest.mark.parametrize("comment_id", [1, 100, 250, 400, 500])
    def test_get_comment_by_id(self, rest_client, comments_endpoint, comment_id):
        """Получение комментария по ID."""
        response = rest_client.get(f"{comments_endpoint}/{comment_id}")
        
        assert_status_code(response, HTTPStatus.OK)
        comment = response.json()
        assert_field_equals(comment, "id", comment_id)
    
    @allure.story("Get Comments By Post")
    @pytest.mark.parametrize("post_id", [1, 10, 50, 100])
    def test_get_comments_by_post_id(self, rest_client, comments_endpoint, post_id):
        """Получение комментариев к посту."""
        response = rest_client.get(comments_endpoint, params={"postId": post_id})
        
        assert_status_code(response, HTTPStatus.OK)
        comments = response.json()
        
        assert_list_not_empty(comments)
        for comment in comments:
            assert_field_equals(comment, "postId", post_id)
    
    @allure.story("Get Comments By Post")
    def test_each_post_has_5_comments(self, rest_client, comments_endpoint):
        """Каждый пост имеет 5 комментариев."""
        response = rest_client.get(comments_endpoint, params={"postId": 1})
        comments = response.json()
        
        assert len(comments) == 5, "Каждый пост имеет ровно 5 комментариев"


@allure.epic("REST API")
@allure.feature("Comments")
class TestCommentsCreate:
    """POST операции - создание комментариев."""
    
    @allure.story("Create Comment")
    @pytest.mark.smoke
    def test_create_comment(self, rest_client, comments_endpoint, random_comment):
        """Создание нового комментария."""
        response = rest_client.post(comments_endpoint, json=random_comment)
        
        assert_status_code(response, HTTPStatus.CREATED)
        created = response.json()
        
        assert "id" in created
        assert created["name"] == random_comment.name
    
    @allure.story("Create Comment")
    @pytest.mark.parametrize("post_id", [1, 50, 100])
    def test_create_comment_for_post(self, rest_client, comments_endpoint, data_generator, post_id):
        """Создание комментария к конкретному посту."""
        comment = data_generator.comment_create(post_id=post_id)
        response = rest_client.post(comments_endpoint, json=comment)
        
        assert_status_code(response, HTTPStatus.CREATED)
        created = response.json()
        assert_field_equals(created, "postId", post_id)


@allure.epic("REST API")
@allure.feature("Comments")
class TestCommentsUpdate:
    """PUT/PATCH операции - обновление комментариев."""
    
    @allure.story("Update Comment")
    def test_update_comment_put(self, rest_client, comments_endpoint):
        """Полное обновление комментария."""
        update_data = {
            "id": 1,
            "postId": 1,
            "name": "Updated Comment",
            "email": "updated@test.com",
            "body": "Updated body",
        }
        response = rest_client.put(f"{comments_endpoint}/1", json=update_data)
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated["name"] == "Updated Comment"
    
    @allure.story("Update Comment")
    def test_update_comment_patch(self, rest_client, comments_endpoint):
        """Частичное обновление комментария."""
        patch_data = {"body": "Patched body"}
        response = rest_client.patch(f"{comments_endpoint}/1", json=patch_data)
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated["body"] == "Patched body"


@allure.epic("REST API")
@allure.feature("Comments")
class TestCommentsDelete:
    """DELETE операции - удаление комментариев."""
    
    @allure.story("Delete Comment")
    def test_delete_comment(self, rest_client, comments_endpoint):
        """Удаление комментария."""
        response = rest_client.delete(f"{comments_endpoint}/1")
        assert_status_code(response, HTTPStatus.OK)


@allure.epic("REST API")
@allure.feature("Comments")
class TestCommentsNegative:
    """Негативные тесты для Comments API."""
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_get_nonexistent_comment(self, rest_client, comments_endpoint):
        """Запрос несуществующего комментария."""
        response = rest_client.get(f"{comments_endpoint}/999999")
        assert_status_code(response, HTTPStatus.NOT_FOUND)
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_get_comments_nonexistent_post(self, rest_client, comments_endpoint):
        """Комментарии несуществующего поста."""
        response = rest_client.get(comments_endpoint, params={"postId": 99999})
        
        assert_status_code(response, HTTPStatus.OK)
        comments = response.json()
        assert len(comments) == 0






