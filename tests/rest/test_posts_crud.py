"""
CRUD тесты для Posts API.
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
    assert_list_length,
)
from src.models.post import Post


@allure.epic("REST API")
@allure.feature("Posts")
class TestPostsGet:
    """GET операции с постами."""
    
    @allure.story("Get All Posts")
    @pytest.mark.smoke
    def test_get_all_posts(self, rest_client, posts_endpoint):
        """Получение списка всех постов."""
        response = rest_client.get(posts_endpoint)
        
        assert_status_code(response, HTTPStatus.OK)
        posts = response.json()
        
        assert_list_not_empty(posts)
        assert_list_length(posts, 100, "JSONPlaceholder имеет 100 постов")
    
    @allure.story("Get All Posts")
    def test_get_all_posts_structure(self, rest_client, posts_endpoint):
        """Проверка структуры ответа списка постов."""
        response = rest_client.get(posts_endpoint)
        posts = response.json()
        
        required_keys = ["id", "userId", "title", "body"]
        for post in posts[:5]:  # Проверяем первые 5
            assert_contains_keys(post, required_keys)
    
    @allure.story("Get Post By ID")
    @pytest.mark.parametrize("post_id", [1, 25, 50, 75, 100])
    def test_get_post_by_id(self, rest_client, posts_endpoint, post_id):
        """Получение поста по ID."""
        response = rest_client.get(f"{posts_endpoint}/{post_id}")
        
        assert_status_code(response, HTTPStatus.OK)
        post = response.json()
        assert_field_equals(post, "id", post_id)
    
    @allure.story("Get Post By ID")
    def test_get_post_validates_with_model(self, rest_client, posts_endpoint):
        """Валидация ответа через Pydantic модель."""
        response = rest_client.get(f"{posts_endpoint}/1")
        post_data = response.json()
        
        post = Post.model_validate(post_data)
        assert post.id == 1
        assert post.userId > 0
    
    @allure.story("Get Posts By User")
    @pytest.mark.parametrize("user_id", [1, 2, 5, 10])
    def test_get_posts_by_user_id(self, rest_client, posts_endpoint, user_id):
        """Получение постов конкретного пользователя."""
        response = rest_client.get(posts_endpoint, params={"userId": user_id})
        
        assert_status_code(response, HTTPStatus.OK)
        posts = response.json()
        
        assert_list_not_empty(posts)
        for post in posts:
            assert_field_equals(post, "userId", user_id)
    
    @allure.story("Get Post Comments")
    def test_get_post_comments(self, rest_client, posts_endpoint):
        """Получение комментариев к посту."""
        response = rest_client.get(f"{posts_endpoint}/1/comments")
        
        assert_status_code(response, HTTPStatus.OK)
        comments = response.json()
        
        assert_list_not_empty(comments)
        for comment in comments:
            assert_field_equals(comment, "postId", 1)


@allure.epic("REST API")
@allure.feature("Posts")
class TestPostsCreate:
    """POST операции - создание постов."""
    
    @allure.story("Create Post")
    @pytest.mark.smoke
    def test_create_post(self, rest_client, posts_endpoint, random_post):
        """Создание нового поста."""
        response = rest_client.post(posts_endpoint, json=random_post)
        
        assert_status_code(response, HTTPStatus.CREATED)
        created = response.json()
        
        assert "id" in created
        assert created["title"] == random_post.title
        assert created["body"] == random_post.body
    
    @allure.story("Create Post")
    def test_create_post_returns_id(self, rest_client, posts_endpoint, random_post):
        """Проверка что при создании поста возвращается ID."""
        response = rest_client.post(posts_endpoint, json=random_post)
        created = response.json()
        
        assert "id" in created
        assert created["id"] == 101
    
    @allure.story("Create Post")
    @pytest.mark.parametrize("user_id", [1, 5, 10])
    def test_create_post_for_user(self, rest_client, posts_endpoint, data_generator, user_id):
        """Создание поста для конкретного пользователя."""
        post = data_generator.post_create(user_id=user_id)
        response = rest_client.post(posts_endpoint, json=post)
        
        assert_status_code(response, HTTPStatus.CREATED)
        created = response.json()
        assert_field_equals(created, "userId", user_id)


@allure.epic("REST API")
@allure.feature("Posts")
class TestPostsUpdate:
    """PUT/PATCH операции - обновление постов."""
    
    @allure.story("Update Post")
    @pytest.mark.smoke
    def test_update_post_put(self, rest_client, posts_endpoint):
        """Полное обновление поста (PUT)."""
        update_data = {
            "id": 1,
            "userId": 1,
            "title": "Updated Title",
            "body": "Updated body content",
        }
        response = rest_client.put(f"{posts_endpoint}/1", json=update_data)
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated["title"] == "Updated Title"
    
    @allure.story("Update Post")
    def test_update_post_patch(self, rest_client, posts_endpoint):
        """Частичное обновление поста (PATCH)."""
        patch_data = {"title": "Patched Title"}
        response = rest_client.patch(f"{posts_endpoint}/1", json=patch_data)
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated["title"] == "Patched Title"
    
    @allure.story("Update Post")
    @pytest.mark.parametrize("field,value", [
        ("title", "New Title Here"),
        ("body", "New body content here"),
    ])
    def test_update_post_single_field(self, rest_client, posts_endpoint, field, value):
        """Обновление отдельных полей поста."""
        response = rest_client.patch(f"{posts_endpoint}/1", json={field: value})
        
        assert_status_code(response, HTTPStatus.OK)
        updated = response.json()
        assert updated[field] == value


@allure.epic("REST API")
@allure.feature("Posts")
class TestPostsDelete:
    """DELETE операции - удаление постов."""
    
    @allure.story("Delete Post")
    @pytest.mark.smoke
    def test_delete_post(self, rest_client, posts_endpoint):
        """Удаление поста."""
        response = rest_client.delete(f"{posts_endpoint}/1")
        assert_status_code(response, HTTPStatus.OK)
    
    @allure.story("Delete Post")
    @pytest.mark.parametrize("post_id", [1, 50, 100])
    def test_delete_different_posts(self, rest_client, posts_endpoint, post_id):
        """Удаление разных постов."""
        response = rest_client.delete(f"{posts_endpoint}/{post_id}")
        assert_status_code(response, HTTPStatus.OK)


@allure.epic("REST API")
@allure.feature("Posts")
class TestPostsNegative:
    """Негативные тесты для Posts API."""
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_get_nonexistent_post(self, rest_client, posts_endpoint):
        """Запрос несуществующего поста."""
        response = rest_client.get(f"{posts_endpoint}/999999")
        assert_status_code(response, HTTPStatus.NOT_FOUND)
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_get_posts_invalid_user_filter(self, rest_client, posts_endpoint):
        """Фильтр постов по несуществующему пользователю."""
        response = rest_client.get(posts_endpoint, params={"userId": 99999})
        
        assert_status_code(response, HTTPStatus.OK)
        posts = response.json()
        assert len(posts) == 0  # Должен вернуть пустой список







