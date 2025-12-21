"""Кастомные assertions для API тестирования."""
from typing import Any, Type
from http import HTTPStatus
import httpx
import jsonschema
from pydantic import BaseModel
import allure


def assert_status_code(
    response: httpx.Response,
    expected: int | HTTPStatus,
    message: str = "",
) -> None:
    """
    Проверить HTTP статус код.
    
    Args:
        response: HTTP ответ
        expected: Ожидаемый статус код
        message: Дополнительное сообщение об ошибке
    """
    expected_code = expected.value if isinstance(expected, HTTPStatus) else expected
    
    with allure.step(f"Проверка статус кода: ожидается {expected_code}"):
        actual = response.status_code
        error_msg = (
            f"Статус код {actual} != {expected_code}. "
            f"{message}\n"
            f"Response: {response.text[:500]}"
        )
        assert actual == expected_code, error_msg


def assert_json_schema(
    data: dict | list,
    schema: dict,
    message: str = "",
) -> None:
    """
    Валидация JSON по схеме.
    
    Args:
        data: JSON данные для валидации
        schema: JSON Schema
        message: Дополнительное сообщение
    """
    with allure.step("Валидация JSON Schema"):
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            raise AssertionError(f"JSON Schema validation failed: {e.message}. {message}")


def assert_response_time(
    response: httpx.Response,
    max_seconds: float,
    message: str = "",
) -> None:
    """
    Проверить время ответа.
    
    Args:
        response: HTTP ответ
        max_seconds: Максимальное время в секундах
        message: Дополнительное сообщение
    """
    with allure.step(f"Проверка времени ответа: < {max_seconds}s"):
        elapsed = response.elapsed.total_seconds()
        assert elapsed < max_seconds, (
            f"Response time {elapsed:.2f}s > {max_seconds}s. {message}"
        )


def assert_contains_keys(
    data: dict,
    keys: list[str],
    message: str = "",
) -> None:
    """
    Проверить наличие ключей в словаре.
    
    Args:
        data: Словарь для проверки
        keys: Список обязательных ключей
        message: Дополнительное сообщение
    """
    with allure.step(f"Проверка наличия ключей: {keys}"):
        missing = [key for key in keys if key not in data]
        assert not missing, (
            f"Missing keys: {missing}. Got keys: {list(data.keys())}. {message}"
        )


def assert_model_valid(
    data: dict,
    model: Type[BaseModel],
    message: str = "",
) -> BaseModel:
    """
    Валидация данных через Pydantic модель.
    
    Args:
        data: Данные для валидации
        model: Pydantic модель
        message: Дополнительное сообщение
    
    Returns:
        Экземпляр модели
    """
    with allure.step(f"Валидация через модель {model.__name__}"):
        try:
            return model.model_validate(data)
        except Exception as e:
            raise AssertionError(f"Model validation failed: {e}. {message}")


def assert_list_not_empty(data: list, message: str = "") -> None:
    """Проверить что список не пустой."""
    with allure.step("Проверка что список не пустой"):
        assert len(data) > 0, f"List is empty. {message}"


def assert_list_length(
    data: list,
    expected_length: int,
    message: str = "",
) -> None:
    """Проверить длину списка."""
    with allure.step(f"Проверка длины списка: ожидается {expected_length}"):
        actual = len(data)
        assert actual == expected_length, (
            f"List length {actual} != {expected_length}. {message}"
        )


def assert_list_length_range(
    data: list,
    min_length: int,
    max_length: int,
    message: str = "",
) -> None:
    """Проверить что длина списка в диапазоне."""
    with allure.step(f"Проверка длины списка: {min_length} <= len <= {max_length}"):
        actual = len(data)
        assert min_length <= actual <= max_length, (
            f"List length {actual} not in range [{min_length}, {max_length}]. {message}"
        )


def assert_field_equals(
    data: dict,
    field: str,
    expected: Any,
    message: str = "",
) -> None:
    """Проверить значение поля."""
    with allure.step(f"Проверка поля {field} == {expected}"):
        actual = data.get(field)
        assert actual == expected, (
            f"Field '{field}' value {actual} != {expected}. {message}"
        )


def assert_field_in(
    data: dict,
    field: str,
    expected_values: list[Any],
    message: str = "",
) -> None:
    """Проверить что значение поля в списке допустимых."""
    with allure.step(f"Проверка поля {field} в {expected_values}"):
        actual = data.get(field)
        assert actual in expected_values, (
            f"Field '{field}' value {actual} not in {expected_values}. {message}"
        )


def assert_error_response(
    response: httpx.Response,
    expected_status: int | HTTPStatus,
    error_field: str = "error",
) -> dict:
    """
    Проверить ошибочный ответ API.
    
    Args:
        response: HTTP ответ
        expected_status: Ожидаемый статус код
        error_field: Поле с ошибкой в JSON
    
    Returns:
        JSON тело ответа
    """
    assert_status_code(response, expected_status)
    
    with allure.step(f"Проверка наличия поля ошибки '{error_field}'"):
        data = response.json()
        assert error_field in data, f"Error field '{error_field}' not found in response"
        return data







