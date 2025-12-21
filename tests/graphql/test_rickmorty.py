"""
GraphQL тесты для Rick and Morty API.
https://rickandmortyapi.com/graphql
"""
import pytest
import allure


@allure.epic("GraphQL API")
@allure.feature("Rick and Morty")
class TestCharactersQueries:
    """Запросы персонажей."""
    
    @allure.story("Get Characters")
    @pytest.mark.smoke
    def test_get_characters(self, graphql_rickmorty_client, rickmorty_characters_query):
        """Получение списка персонажей."""
        result = graphql_rickmorty_client.query(
            rickmorty_characters_query,
            variables={"page": 1}
        )
        
        characters = result["characters"]
        assert characters["info"]["count"] > 0
        assert len(characters["results"]) > 0
    
    @allure.story("Get Characters")
    def test_characters_pagination_info(self, graphql_rickmorty_client, rickmorty_characters_query):
        """Информация о пагинации персонажей."""
        result = graphql_rickmorty_client.query(
            rickmorty_characters_query,
            variables={"page": 1}
        )
        
        info = result["characters"]["info"]
        assert info["count"] > 800
        assert info["pages"] > 40
        assert info["next"] == 2
        assert info["prev"] is None
    
    @allure.story("Get Characters")
    @pytest.mark.parametrize("page", [1, 2, 5, 10])
    def test_characters_different_pages(self, graphql_rickmorty_client, rickmorty_characters_query, page):
        """Пагинация персонажей."""
        result = graphql_rickmorty_client.query(
            rickmorty_characters_query,
            variables={"page": page}
        )
        
        characters = result["characters"]["results"]
        assert len(characters) == 20
    
    @allure.story("Get Single Character")
    @pytest.mark.parametrize("char_id,expected_name", [
        ("1", "Rick Sanchez"),
        ("2", "Morty Smith"),
        ("3", "Summer Smith"),
        ("4", "Beth Smith"),
        ("5", "Jerry Smith"),
    ])
    def test_get_character_by_id(self, graphql_rickmorty_client, rickmorty_character_query, char_id, expected_name):
        """Получение персонажа по ID."""
        result = graphql_rickmorty_client.query(
            rickmorty_character_query,
            variables={"id": char_id}
        )
        
        character = result["character"]
        assert character is not None
        assert character["name"] == expected_name
    
    @allure.story("Get Single Character")
    def test_character_has_episodes(self, graphql_rickmorty_client, rickmorty_character_query):
        """Персонаж содержит эпизоды."""
        result = graphql_rickmorty_client.query(
            rickmorty_character_query,
            variables={"id": "1"}
        )
        
        character = result["character"]
        episodes = character["episode"]
        
        assert len(episodes) > 0
    
    @allure.story("Get Single Character")
    def test_character_has_origin_and_location(self, graphql_rickmorty_client, rickmorty_character_query):
        """Персонаж содержит origin и location."""
        result = graphql_rickmorty_client.query(
            rickmorty_character_query,
            variables={"id": "1"}
        )
        
        character = result["character"]
        assert character["origin"]["name"] is not None
        assert character["location"]["name"] is not None


@allure.epic("GraphQL API")
@allure.feature("Rick and Morty")
class TestEpisodesQueries:
    """Запросы эпизодов."""
    
    @allure.story("Get Episodes")
    @pytest.mark.smoke
    def test_get_episodes(self, graphql_rickmorty_client, rickmorty_episodes_query):
        """Получение списка эпизодов."""
        result = graphql_rickmorty_client.query(
            rickmorty_episodes_query,
            variables={"page": 1}
        )
        
        episodes = result["episodes"]
        assert episodes["info"]["count"] > 0
        assert len(episodes["results"]) > 0
    
    @allure.story("Get Episodes")
    def test_episodes_have_episode_code(self, graphql_rickmorty_client, rickmorty_episodes_query):
        """Эпизоды содержат код эпизода."""
        result = graphql_rickmorty_client.query(
            rickmorty_episodes_query,
            variables={"page": 1}
        )
        
        episodes = result["episodes"]["results"]
        
        assert episodes[0]["episode"] == "S01E01"
    
    @allure.story("Get Episodes")
    def test_episodes_have_air_date(self, graphql_rickmorty_client, rickmorty_episodes_query):
        """Эпизоды содержат дату выхода."""
        result = graphql_rickmorty_client.query(
            rickmorty_episodes_query,
            variables={"page": 1}
        )
        
        for episode in result["episodes"]["results"]:
            assert episode["air_date"] is not None


@allure.epic("GraphQL API")
@allure.feature("Rick and Morty")
class TestLocationsQueries:
    """Запросы локаций."""
    
    @allure.story("Get Locations")
    @pytest.mark.smoke
    def test_get_locations(self, graphql_rickmorty_client, rickmorty_locations_query):
        """Получение списка локаций."""
        result = graphql_rickmorty_client.query(
            rickmorty_locations_query,
            variables={"page": 1}
        )
        
        locations = result["locations"]
        assert locations["info"]["count"] > 0
        assert len(locations["results"]) > 0
    
    @allure.story("Get Locations")
    def test_locations_have_dimension(self, graphql_rickmorty_client, rickmorty_locations_query):
        """Локации содержат измерение."""
        result = graphql_rickmorty_client.query(
            rickmorty_locations_query,
            variables={"page": 1}
        )
        
        for location in result["locations"]["results"][:5]:
            assert "dimension" in location


@allure.epic("GraphQL API")
@allure.feature("Rick and Morty")
class TestRickMortyFilter:
    """Тесты фильтрации."""
    
    @allure.story("Filter Characters")
    def test_filter_characters_by_status(self, graphql_rickmorty_client):
        """Фильтрация персонажей по статусу."""
        query = """
        query {
            characters(filter: { status: "Dead" }) {
                results {
                    name
                    status
                }
            }
        }
        """
        result = graphql_rickmorty_client.query(query)
        
        characters = result["characters"]["results"]
        assert len(characters) > 0
        
        for char in characters:
            assert char["status"] == "Dead"
    
    @allure.story("Filter Characters")
    def test_filter_characters_by_species(self, graphql_rickmorty_client):
        """Фильтрация персонажей по виду."""
        query = """
        query {
            characters(filter: { species: "Alien" }) {
                results {
                    name
                    species
                }
            }
        }
        """
        result = graphql_rickmorty_client.query(query)
        
        characters = result["characters"]["results"]
        assert len(characters) > 0
        
        for char in characters:
            assert char["species"] == "Alien"
    
    @allure.story("Filter Characters")
    def test_filter_characters_by_name(self, graphql_rickmorty_client):
        """Поиск персонажей по имени."""
        query = """
        query {
            characters(filter: { name: "Rick" }) {
                results {
                    name
                }
            }
        }
        """
        result = graphql_rickmorty_client.query(query)
        
        characters = result["characters"]["results"]
        assert len(characters) > 0
        
        for char in characters:
            assert "Rick" in char["name"]


@allure.epic("GraphQL API")
@allure.feature("Rick and Morty")
class TestRickMortyNegative:
    """Негативные тесты."""
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_nonexistent_character(self, graphql_rickmorty_client, rickmorty_character_query):
        """Запрос несуществующего персонажа."""
        result = graphql_rickmorty_client.query(
            rickmorty_character_query,
            variables={"id": "999999"}
        )
        
        assert result["character"] is None
    
    @allure.story("Negative Cases")
    @pytest.mark.negative
    def test_invalid_page_number(self, graphql_rickmorty_client, rickmorty_characters_query):
        """Запрос невалидного номера страницы."""
        result = graphql_rickmorty_client.query(
            rickmorty_characters_query,
            variables={"page": 99999}
        )
        
        characters = result["characters"]
        assert characters["results"] is None or len(characters["results"]) == 0






