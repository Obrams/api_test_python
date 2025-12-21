"""
Тесты обработки ошибок GraphQL.
"""
import pytest
import allure
from http import HTTPStatus


@allure.epic("GraphQL API")
@allure.feature("Error Handling")
class TestGraphQLErrors:
    """Тесты обработки ошибок GraphQL."""
    
    @allure.story("Syntax Errors")
    @pytest.mark.negative
    def test_invalid_query_syntax(self, graphql_countries_client):
        """Невалидный синтаксис запроса."""
        invalid_query = """
        query {
            countries {
                invalid syntax here
            }
        }
        """
        
        with pytest.raises(Exception):
            graphql_countries_client.query(invalid_query)
    
    @allure.story("Syntax Errors")
    @pytest.mark.negative
    def test_unclosed_braces(self, graphql_countries_client):
        """Незакрытые скобки."""
        invalid_query = """
        query {
            countries {
                code
                name
        """
        
        with pytest.raises(Exception):
            graphql_countries_client.query(invalid_query)
    
    @allure.story("Field Errors")
    @pytest.mark.negative
    def test_nonexistent_field(self, graphql_countries_client):
        """Запрос несуществующего поля."""
        query = """
        query {
            countries {
                code
                nonexistentField
            }
        }
        """
        
        with pytest.raises(Exception):
            graphql_countries_client.query(query)
    
    @allure.story("Field Errors")
    @pytest.mark.negative
    def test_nonexistent_query(self, graphql_countries_client):
        """Запрос несуществующего query."""
        query = """
        query {
            nonexistentQuery {
                id
            }
        }
        """
        
        with pytest.raises(Exception):
            graphql_countries_client.query(query)
    
    @allure.story("Variable Errors")
    @pytest.mark.negative
    def test_missing_required_variable(self, graphql_countries_client, country_by_code_query):
        """Отсутствует обязательная переменная."""
        with pytest.raises(Exception):
            graphql_countries_client.query(country_by_code_query, variables={})
    
    @allure.story("Variable Errors")
    @pytest.mark.negative
    def test_wrong_variable_type(self, graphql_countries_client):
        """Неверный тип переменной."""
        query = """
        query GetCountry($code: Int!) {
            country(code: $code) {
                name
            }
        }
        """
        
        with pytest.raises(Exception):
            graphql_countries_client.query(query, variables={"code": 123})


@allure.epic("GraphQL API")
@allure.feature("Error Handling")
class TestRawRequests:
    """Тесты через raw HTTP запросы."""
    
    @allure.story("Raw Requests")
    def test_raw_request_success(self, graphql_countries_client):
        """Успешный raw запрос."""
        query = """
        query {
            countries {
                code
            }
        }
        """
        
        response = graphql_countries_client.raw_request(query)
        
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "data" in data
        assert "errors" not in data
    
    @allure.story("Raw Requests")
    @pytest.mark.negative
    def test_raw_request_with_errors(self, graphql_countries_client):
        """Raw запрос с ошибками."""
        query = """
        query {
            invalidQuery {
                id
            }
        }
        """
        
        response = graphql_countries_client.raw_request(query)
        
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "errors" in data
    
    @allure.story("Raw Requests")
    @pytest.mark.negative
    def test_raw_request_empty_query(self, graphql_countries_client):
        """Пустой запрос."""
        response = graphql_countries_client.raw_request("")
        
        data = response.json()
        assert "errors" in data or data.get("data") is None







