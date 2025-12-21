"""Фикстуры специфичные для GraphQL тестов."""
import pytest


@pytest.fixture
def countries_query():
    """Базовый запрос стран."""
    return """
    query {
        countries {
            code
            name
            capital
        }
    }
    """


@pytest.fixture
def country_by_code_query():
    """Запрос страны по коду."""
    return """
    query GetCountry($code: ID!) {
        country(code: $code) {
            code
            name
            capital
            currency
            phone
            languages {
                code
                name
            }
        }
    }
    """


@pytest.fixture
def continents_query():
    """Запрос континентов."""
    return """
    query {
        continents {
            code
            name
            countries {
                code
                name
            }
        }
    }
    """


@pytest.fixture
def languages_query():
    """Запрос языков."""
    return """
    query {
        languages {
            code
            name
            native
        }
    }
    """


@pytest.fixture
def rickmorty_characters_query():
    """Запрос персонажей Rick and Morty."""
    return """
    query GetCharacters($page: Int) {
        characters(page: $page) {
            info {
                count
                pages
                next
                prev
            }
            results {
                id
                name
                status
                species
                gender
                image
            }
        }
    }
    """


@pytest.fixture
def rickmorty_character_query():
    """Запрос одного персонажа Rick and Morty."""
    return """
    query GetCharacter($id: ID!) {
        character(id: $id) {
            id
            name
            status
            species
            type
            gender
            origin {
                name
            }
            location {
                name
            }
            image
            episode {
                id
                name
            }
        }
    }
    """


@pytest.fixture
def rickmorty_episodes_query():
    """Запрос эпизодов Rick and Morty."""
    return """
    query GetEpisodes($page: Int) {
        episodes(page: $page) {
            info {
                count
                pages
            }
            results {
                id
                name
                air_date
                episode
            }
        }
    }
    """


@pytest.fixture
def rickmorty_locations_query():
    """Запрос локаций Rick and Morty."""
    return """
    query GetLocations($page: Int) {
        locations(page: $page) {
            info {
                count
                pages
            }
            results {
                id
                name
                type
                dimension
            }
        }
    }
    """






