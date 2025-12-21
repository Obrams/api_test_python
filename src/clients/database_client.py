"""Database client for PostgreSQL operations."""
from typing import Any, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, text, select, func, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from src.database.base import Base
from src.database.models import UserDB, PostDB, CommentDB, APILogDB


class DatabaseClient:
    """
    Клиент для работы с PostgreSQL.
    
    Примеры использования:
        >>> db = DatabaseClient("postgresql://user:pass@localhost/db")
        >>> db.create_tables()
        >>> 
        >>> # Сохранение данных
        >>> db.save_user({"name": "John", "email": "john@example.com"})
        >>> 
        >>> # SQL запросы
        >>> user = db.query_one("SELECT * FROM users WHERE id = :id", {"id": 1})
        >>> users = db.query_all("SELECT * FROM users WHERE name LIKE :name", {"name": "%John%"})
        >>> 
        >>> # Cleanup
        >>> db.truncate_all()
        >>> db.close()
    """
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Инициализация клиента.
        
        Args:
            database_url: PostgreSQL connection string
            echo: Включить логирование SQL запросов
        """
        self._engine: Engine = create_engine(database_url, echo=echo)
        self._session_factory = sessionmaker(bind=self._engine)
    
    @property
    def engine(self) -> Engine:
        """SQLAlchemy Engine."""
        return self._engine
    
    def _validate_table_name(self, table_name: str) -> Table:
        """
        Валидировать и получить объект таблицы из metadata.
        
        Args:
            table_name: Имя таблицы
            
        Returns:
            SQLAlchemy Table объект
            
        Raises:
            ValueError: Если таблица не найдена в metadata
        """
        table = Base.metadata.tables.get(table_name)
        if table is None:
            available_tables = list(Base.metadata.tables.keys())
            raise ValueError(
                f"Unknown table: '{table_name}'. "
                f"Available tables: {available_tables}"
            )
        return table
    
    @contextmanager
    def session(self):
        """Context manager для сессии."""
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # =====================
    # Schema Management
    # =====================
    
    def create_tables(self) -> None:
        """Создать все таблицы в БД."""
        Base.metadata.create_all(self._engine)
    
    def drop_tables(self) -> None:
        """Удалить все таблицы из БД."""
        Base.metadata.drop_all(self._engine)
    
    def truncate_all(self) -> None:
        """Очистить все таблицы (TRUNCATE CASCADE)."""
        with self.session() as session:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))
    
    def truncate_table(self, table_name: str) -> None:
        """
        Очистить конкретную таблицу.
        
        Args:
            table_name: Имя таблицы (валидируется через metadata)
            
        Raises:
            ValueError: Если таблица не найдена в metadata
        """
        # Валидация имени таблицы для предотвращения SQL Injection
        table = self._validate_table_name(table_name)
        
        with self.session() as session:
            # Используем безопасное имя таблицы из metadata
            session.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))
    
    # =====================
    # Raw SQL Queries
    # =====================
    
    def execute(self, query: str, params: Optional[dict[str, Any]] = None) -> None:
        """
        Выполнить SQL запрос без возврата данных.
        
        Args:
            query: SQL запрос с именованными параметрами (:param)
            params: Словарь параметров
        """
        with self.session() as session:
            session.execute(text(query), params or {})
    
    def query_one(self, query: str, params: Optional[dict[str, Any]] = None) -> Optional[dict[str, Any]]:
        """
        Выполнить SQL запрос и вернуть одну строку.
        
        Args:
            query: SQL запрос с именованными параметрами (:param)
            params: Словарь параметров
            
        Returns:
            Словарь с данными строки или None
        """
        with self.session() as session:
            result = session.execute(text(query), params or {})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None
    
    def query_all(self, query: str, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """
        Выполнить SQL запрос и вернуть все строки.
        
        Args:
            query: SQL запрос с именованными параметрами (:param)
            params: Словарь параметров
            
        Returns:
            Список словарей с данными
        """
        with self.session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result.fetchall()]
    
    def count(self, table: str, conditions: Optional[dict[str, Any]] = None) -> int:
        """
        Подсчитать количество строк в таблице.
        
        Args:
            table: Имя таблицы (валидируется через metadata)
            conditions: Условия WHERE (column: value)
            
        Returns:
            Количество строк
            
        Raises:
            ValueError: Если таблица не найдена или колонка не существует
        """
        # Валидация имени таблицы для предотвращения SQL Injection
        table_obj = self._validate_table_name(table)
        
        # Построение безопасного запроса через SQLAlchemy
        stmt = select(func.count()).select_from(table_obj)
        
        # Безопасное добавление условий WHERE
        if conditions:
            for column_name, value in conditions.items():
                # Валидация имени колонки
                if column_name not in table_obj.c:
                    available_columns = list(table_obj.c.keys())
                    raise ValueError(
                        f"Unknown column '{column_name}' in table '{table}'. "
                        f"Available columns: {available_columns}"
                    )
                # Используем безопасную ссылку на колонку из metadata
                stmt = stmt.where(table_obj.c[column_name] == value)
        
        with self.session() as session:
            result = session.scalar(stmt)
            return result if result is not None else 0
    
    # =====================
    # ORM Operations - Users
    # =====================
    
    def save_user(self, data: dict[str, Any]) -> UserDB:
        """
        Сохранить пользователя в БД.
        
        Args:
            data: Данные пользователя (из API response)
            
        Returns:
            Созданный объект UserDB
        """
        with self.session() as session:
            user = UserDB(
                external_id=data.get("id"),
                name=data.get("name", ""),
                email=data.get("email", ""),
                username=data.get("username"),
                phone=data.get("phone"),
                website=data.get("website"),
            )
            session.add(user)
            session.flush()
            session.refresh(user)
            return user
    
    def get_user(self, user_id: int) -> Optional[UserDB]:
        """Получить пользователя по ID."""
        with self.session() as session:
            return session.get(UserDB, user_id)
    
    def get_user_by_external_id(self, external_id: int) -> Optional[dict[str, Any]]:
        """Получить пользователя по external_id (ID из API)."""
        return self.query_one(
            "SELECT * FROM users WHERE external_id = :external_id",
            {"external_id": external_id}
        )
    
    # =====================
    # ORM Operations - Posts
    # =====================
    
    def save_post(self, data: dict[str, Any]) -> PostDB:
        """
        Сохранить пост в БД.
        
        Args:
            data: Данные поста (из API response)
            
        Returns:
            Созданный объект PostDB
        """
        with self.session() as session:
            post = PostDB(
                external_id=data.get("id"),
                user_id=data.get("userId"),
                title=data.get("title", ""),
                body=data.get("body", ""),
            )
            session.add(post)
            session.flush()
            session.refresh(post)
            return post
    
    def get_post(self, post_id: int) -> Optional[PostDB]:
        """Получить пост по ID."""
        with self.session() as session:
            return session.get(PostDB, post_id)
    
    def get_post_by_external_id(self, external_id: int) -> Optional[dict[str, Any]]:
        """Получить пост по external_id (ID из API)."""
        return self.query_one(
            "SELECT * FROM posts WHERE external_id = :external_id",
            {"external_id": external_id}
        )
    
    # =====================
    # ORM Operations - Comments
    # =====================
    
    def save_comment(self, data: dict[str, Any]) -> CommentDB:
        """
        Сохранить комментарий в БД.
        
        Args:
            data: Данные комментария (из API response)
            
        Returns:
            Созданный объект CommentDB
        """
        with self.session() as session:
            comment = CommentDB(
                external_id=data.get("id"),
                post_id=data.get("postId"),
                name=data.get("name", ""),
                email=data.get("email", ""),
                body=data.get("body", ""),
            )
            session.add(comment)
            session.flush()
            session.refresh(comment)
            return comment
    
    def get_comment(self, comment_id: int) -> Optional[CommentDB]:
        """Получить комментарий по ID."""
        with self.session() as session:
            return session.get(CommentDB, comment_id)
    
    # =====================
    # ORM Operations - API Logs
    # =====================
    
    def log_api_call(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        request_headers: Optional[dict] = None,
        request_body: Optional[dict] = None,
        response_headers: Optional[dict] = None,
        response_body: Optional[dict] = None,
        duration_ms: Optional[float] = None,
        test_name: Optional[str] = None,
    ) -> APILogDB:
        """
        Залогировать API вызов в БД.
        
        Args:
            method: HTTP метод
            url: URL запроса
            status_code: HTTP статус код ответа
            request_headers: Заголовки запроса
            request_body: Тело запроса
            response_headers: Заголовки ответа
            response_body: Тело ответа
            duration_ms: Время выполнения в мс
            test_name: Имя теста
            
        Returns:
            Созданный объект APILogDB
        """
        with self.session() as session:
            log = APILogDB(
                method=method,
                url=url,
                status_code=status_code,
                request_headers=request_headers,
                request_body=request_body,
                response_headers=response_headers,
                response_body=response_body,
                duration_ms=duration_ms,
                test_name=test_name,
            )
            session.add(log)
            session.flush()
            session.refresh(log)
            return log
    
    def get_api_logs(
        self,
        method: Optional[str] = None,
        url_contains: Optional[str] = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Получить логи API вызовов.
        
        Args:
            method: Фильтр по HTTP методу
            url_contains: Фильтр по части URL
            limit: Максимальное количество записей
            
        Returns:
            Список логов
        """
        query = "SELECT * FROM api_logs WHERE 1=1"
        params: dict[str, Any] = {}
        
        if method:
            query += " AND method = :method"
            params["method"] = method
        
        if url_contains:
            query += " AND url LIKE :url"
            params["url"] = f"%{url_contains}%"
        
        query += " ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit
        
        return self.query_all(query, params)
    
    # =====================
    # Cleanup
    # =====================
    
    def close(self) -> None:
        """Закрыть соединение с БД."""
        self._engine.dispose()




