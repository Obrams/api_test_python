"""SQL assertion utilities for database verification."""
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.clients.database_client import DatabaseClient


class DatabaseAssertionError(AssertionError):
    """Custom exception for database assertion failures."""


def assert_row_exists(
    db: "DatabaseClient",
    table: str,
    conditions: dict[str, Any],
    message: Optional[str] = None
) -> dict[str, Any]:
    """
    Проверить, что строка существует в таблице.
    
    Args:
        db: DatabaseClient instance
        table: Имя таблицы
        conditions: Условия WHERE (column: value)
        message: Кастомное сообщение об ошибке
        
    Returns:
        Найденная строка
        
    Raises:
        DatabaseAssertionError: Если строка не найдена
        
    Example:
        >>> assert_row_exists(db, "users", {"email": "john@example.com"})
    """
    where_clauses = [f"{k} = :{k}" for k in conditions.keys()]
    query = f"SELECT * FROM {table} WHERE " + " AND ".join(where_clauses)
    
    row = db.query_one(query, conditions)
    
    if row is None:
        error_msg = message or f"Row not found in '{table}' with conditions: {conditions}"
        raise DatabaseAssertionError(error_msg)
    
    return row


def assert_row_not_exists(
    db: "DatabaseClient",
    table: str,
    conditions: dict[str, Any],
    message: Optional[str] = None
) -> None:
    """
    Проверить, что строка НЕ существует в таблице.
    
    Args:
        db: DatabaseClient instance
        table: Имя таблицы
        conditions: Условия WHERE (column: value)
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если строка найдена
        
    Example:
        >>> assert_row_not_exists(db, "users", {"email": "deleted@example.com"})
    """
    where_clauses = [f"{k} = :{k}" for k in conditions.keys()]
    query = f"SELECT * FROM {table} WHERE " + " AND ".join(where_clauses)
    
    row = db.query_one(query, conditions)
    
    if row is not None:
        error_msg = message or f"Row unexpectedly found in '{table}' with conditions: {conditions}"
        raise DatabaseAssertionError(error_msg)


def assert_row_count(
    db: "DatabaseClient",
    table: str,
    expected: int,
    conditions: Optional[dict[str, Any]] = None,
    message: Optional[str] = None
) -> None:
    """
    Проверить количество строк в таблице.
    
    Args:
        db: DatabaseClient instance
        table: Имя таблицы
        expected: Ожидаемое количество
        conditions: Опциональные условия WHERE
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если количество не совпадает
        
    Example:
        >>> assert_row_count(db, "users", 5)
        >>> assert_row_count(db, "posts", 10, conditions={"user_id": 1})
    """
    actual = db.count(table, conditions)
    
    if actual != expected:
        cond_str = f" with conditions {conditions}" if conditions else ""
        error_msg = message or f"Expected {expected} rows in '{table}'{cond_str}, but found {actual}"
        raise DatabaseAssertionError(error_msg)


def assert_row_count_gte(
    db: "DatabaseClient",
    table: str,
    minimum: int,
    conditions: Optional[dict[str, Any]] = None,
    message: Optional[str] = None
) -> None:
    """
    Проверить, что количество строк >= minimum.
    
    Args:
        db: DatabaseClient instance
        table: Имя таблицы
        minimum: Минимальное количество
        conditions: Опциональные условия WHERE
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если количество меньше minimum
    """
    actual = db.count(table, conditions)
    
    if actual < minimum:
        cond_str = f" with conditions {conditions}" if conditions else ""
        error_msg = message or f"Expected at least {minimum} rows in '{table}'{cond_str}, but found {actual}"
        raise DatabaseAssertionError(error_msg)


def assert_field_equals(
    db: "DatabaseClient",
    table: str,
    pk_column: str,
    pk_value: Any,
    field: str,
    expected_value: Any,
    message: Optional[str] = None
) -> None:
    """
    Проверить значение конкретного поля в строке.
    
    Args:
        db: DatabaseClient instance
        table: Имя таблицы
        pk_column: Имя колонки первичного ключа
        pk_value: Значение первичного ключа
        field: Имя проверяемого поля
        expected_value: Ожидаемое значение
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если значение не совпадает
        
    Example:
        >>> assert_field_equals(db, "users", "id", 1, "name", "John Doe")
    """
    row = assert_row_exists(db, table, {pk_column: pk_value})
    actual_value = row.get(field)
    
    if actual_value != expected_value:
        error_msg = message or (
            f"Field '{field}' in '{table}' (where {pk_column}={pk_value}): "
            f"expected '{expected_value}', got '{actual_value}'"
        )
        raise DatabaseAssertionError(error_msg)


def assert_field_contains(
    db: "DatabaseClient",
    table: str,
    pk_column: str,
    pk_value: Any,
    field: str,
    substring: str,
    message: Optional[str] = None
) -> None:
    """
    Проверить, что поле содержит подстроку.
    
    Args:
        db: DatabaseClient instance
        table: Имя таблицы
        pk_column: Имя колонки первичного ключа
        pk_value: Значение первичного ключа
        field: Имя проверяемого поля
        substring: Подстрока для поиска
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если подстрока не найдена
    """
    row = assert_row_exists(db, table, {pk_column: pk_value})
    actual_value = str(row.get(field, ""))
    
    if substring not in actual_value:
        error_msg = message or (
            f"Field '{field}' in '{table}' (where {pk_column}={pk_value}): "
            f"expected to contain '{substring}', but got '{actual_value}'"
        )
        raise DatabaseAssertionError(error_msg)


def assert_user_matches_api(
    db: "DatabaseClient",
    api_data: dict[str, Any],
    message: Optional[str] = None
) -> None:
    """
    Проверить, что пользователь в БД соответствует данным из API.
    
    Args:
        db: DatabaseClient instance
        api_data: Данные пользователя из API
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если данные не совпадают
        
    Example:
        >>> response = rest_client.post("/users", json=user_data)
        >>> db.save_user(response.json())
        >>> assert_user_matches_api(db, response.json())
    """
    external_id = api_data.get("id")
    db_user = db.get_user_by_external_id(external_id)
    
    if db_user is None:
        error_msg = message or f"User with external_id={external_id} not found in database"
        raise DatabaseAssertionError(error_msg)
    
    # Проверяем основные поля
    fields_to_check = ["name", "email", "username"]
    for field in fields_to_check:
        api_value = api_data.get(field)
        db_value = db_user.get(field)
        if api_value and api_value != db_value:
            error_msg = message or (
                f"User field '{field}' mismatch: API='{api_value}', DB='{db_value}'"
            )
            raise DatabaseAssertionError(error_msg)


def assert_post_matches_api(
    db: "DatabaseClient",
    api_data: dict[str, Any],
    message: Optional[str] = None
) -> None:
    """
    Проверить, что пост в БД соответствует данным из API.
    
    Args:
        db: DatabaseClient instance
        api_data: Данные поста из API
        message: Кастомное сообщение об ошибке
        
    Raises:
        DatabaseAssertionError: Если данные не совпадают
    """
    external_id = api_data.get("id")
    db_post = db.get_post_by_external_id(external_id)
    
    if db_post is None:
        error_msg = message or f"Post with external_id={external_id} not found in database"
        raise DatabaseAssertionError(error_msg)
    
    # Проверяем основные поля
    fields_to_check = ["title", "body"]
    for field in fields_to_check:
        api_value = api_data.get(field)
        db_value = db_post.get(field)
        if api_value and api_value != db_value:
            error_msg = message or (
                f"Post field '{field}' mismatch: API='{api_value}', DB='{db_value}'"
            )
            raise DatabaseAssertionError(error_msg)





