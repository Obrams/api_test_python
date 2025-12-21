"""
GraphQL тесты для Countries API.
https://countries.trevorblades.com/graphql
"""
import pytest
import allure


@allure.epic("GraphQL API")
@allure.feature("Countries")
class TestCountriesQueries:
    """Запросы стран."""
    
    @allure.story("Get All Countries")
    @pytest.mark.smoke
    def test_get_all_countries(self, graphql_countries_client, countries_query):
        """Получение списка всех стран."""
        result = graphql_countries_client.query(countries_query)
        
        countries = result["countries"]
        assert len(countries) > 0, "Должны быть страны"
        assert len(countries) > 200, "Должно быть более 200 стран"
    
    @allure.story("Get All Countries")
    def test_countries_have_required_fields(self, graphql_countries_client, countries_query):
        """Страны содержат обязательные поля."""
        result = graphql_countries_client.query(countries_query)
        
        for country in result["countries"][:10]:
            assert "code" in country
            assert "name" in country
            assert len(country["code"]) == 2  # ISO 3166-1 alpha-2
    
    @allure.story("Get Country By Code")
    @pytest.mark.parametrize("code,expected_name", [
        ("US", "United States"),
        ("RU", "Russia"),
        ("DE", "Germany"),
        ("JP", "Japan"),
        ("FR", "France"),
        ("GB", "United Kingdom"),
        ("CN", "China"),
        ("BR", "Brazil"),
        ("IN", "India"),
        ("CA", "Canada"),
    ])
    def test_get_country_by_code(self, graphql_countries_client, country_by_code_query, code, expected_name):
        """Получение страны по коду."""
        result = graphql_countries_client.query(
            country_by_code_query,
            variables={"code": code}
        )
        
        country = result["country"]
        assert country is not None
        assert country["code"] == code
        assert country["name"] == expected_name
    
    @allure.story("Get Country By Code")
    def test_country_has_languages(self, graphql_countries_client, country_by_code_query):
        """Страна содержит информацию о языках."""
        result = graphql_countries_client.query(
            country_by_code_query,
            variables={"code": "CH"}
        )
        
        country = result["country"]
        languages = country["languages"]
        
        # Швейцария имеет минимум 3 официальных языка (немецкий, французский, итальянский)
        assert len(languages) >= 3
    
    @allure.story("Get Country By Code")
    def test_country_has_currency(self, graphql_countries_client, country_by_code_query):
        """Страна содержит валюту."""
        result = graphql_countries_client.query(
            country_by_code_query,
            variables={"code": "US"}
        )
        
        country = result["country"]
        # API может возвращать несколько валют через запятую (USD,USN,USS)
        assert "USD" in country["currency"]
    
    @allure.story("Get Country By Code")
    def test_country_has_phone_code(self, graphql_countries_client, country_by_code_query):
        """Страна содержит телефонный код."""
        result = graphql_countries_client.query(
            country_by_code_query,
            variables={"code": "RU"}
        )
        
        country = result["country"]
        assert country["phone"] == "7"


@allure.epic("GraphQL API")
@allure.feature("Countries")
class TestContinentsQueries:
    """Запросы континентов."""
    
    @allure.story("Get All Continents")
    @pytest.mark.smoke
    def test_get_all_continents(self, graphql_countries_client, continents_query):
        """Получение списка континентов."""
        result = graphql_countries_client.query(continents_query)
        
        continents = result["continents"]
        assert len(continents) == 7, "Должно быть 7 континентов"
    
    @allure.story("Get All Continents")
    @pytest.mark.parametrize("expected_code", ["AF", "AN", "AS", "EU", "NA", "OC", "SA"])
    def test_continent_codes(self, graphql_countries_client, continents_query, expected_code):
        """Проверка кодов континентов."""
        result = graphql_countries_client.query(continents_query)
        
        codes = [c["code"] for c in result["continents"]]
        assert expected_code in codes
    
    @allure.story("Get All Continents")
    def test_continents_have_countries(self, graphql_countries_client, continents_query):
        """Континенты содержат страны."""
        result = graphql_countries_client.query(continents_query)
        
        for continent in result["continents"]:
            if continent["code"] != "AN":  # Антарктида может не иметь стран
                assert len(continent["countries"]) > 0


@allure.epic("GraphQL API")
@allure.feature("Countries")
class TestLanguagesQueries:
    """Запросы языков."""
    
    @allure.story("Get All Languages")
    @pytest.mark.smoke
    def test_get_all_languages(self, graphql_countries_client, languages_query):
        """Получение списка языков."""
        result = graphql_countries_client.query(languages_query)
        
        languages = result["languages"]
        assert len(languages) > 0
        assert len(languages) > 100, "Должно быть более 100 языков"
    
    @allure.story("Get All Languages")
    def test_languages_have_native_name(self, graphql_countries_client, languages_query):
        """Языки содержат нативное название."""
        result = graphql_countries_client.query(languages_query)
        
        for lang in result["languages"][:10]:
            assert "native" in lang


@allure.epic("GraphQL API")
@allure.feature("Countries")
class TestCountriesFilter:
    """Тесты фильтрации стран."""
    
    @allure.story("Filter Countries")
    def test_filter_countries_by_continent(self, graphql_countries_client):
        """Фильтрация стран по континенту."""
        query = """
        query {
            countries(filter: { continent: { eq: "EU" } }) {
                code
                name
                continent {
                    code
                }
            }
        }
        """
        result = graphql_countries_client.query(query)
        
        countries = result["countries"]
        assert len(countries) > 0
        
        for country in countries:
            assert country["continent"]["code"] == "EU"
    
    @allure.story("Filter Countries")
    def test_filter_countries_by_currency(self, graphql_countries_client):
        """Фильтрация стран по валюте."""
        query = """
        query {
            countries(filter: { currency: { eq: "EUR" } }) {
                code
                name
                currency
            }
        }
        """
        result = graphql_countries_client.query(query)
        
        countries = result["countries"]
        assert len(countries) > 0
        
        for country in countries:
            assert "EUR" in country["currency"]


@allure.epic("GraphQL API")
@allure.feature("Countries")
class TestCountriesNegative:
    """Негативные тесты."""
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_nonexistent_country_code(self, graphql_countries_client, country_by_code_query):
        """Запрос несуществующего кода страны."""
        result = graphql_countries_client.query(
            country_by_code_query,
            variables={"code": "XX"}
        )
        
        assert result["country"] is None
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_invalid_country_code_format(self, graphql_countries_client, country_by_code_query):
        """Запрос с невалидным форматом кода."""
        result = graphql_countries_client.query(
            country_by_code_query,
            variables={"code": "INVALID"}
        )
        
        assert result["country"] is None







