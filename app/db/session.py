"""Сессия алхимии."""
from contextlib import asynccontextmanager
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


class PGEngineConnector:
    """Класс постгри, отвечающий за получение сессии.

    Сохраняет Engine по ключу URI. Нужен для кросс
    БД соединения и изоляции базы от скоупа модуля.
    """

    engine_dict: ClassVar[dict[str, AsyncEngine]] = {}
    sql_alchemy_uri: str = None

    def __init__(self, sql_alchemy_uri: str | None = None):
        """Инициализируем объект коннектора.

        Args:
            sql_alchemy_uri: str - строка подключения пг
        """
        from app.config import CONFIG

        if sql_alchemy_uri:
            self.sql_alchemy_uri = sql_alchemy_uri

        else:
            self.sql_alchemy_uri = CONFIG.SQLALCHEMY_DATABASE_URI

    @classmethod
    def get_pg_engine(cls, sql_alchemy_uri: str):
        """Получаем енжин для алхимии. Синглтон.

        Returns:
            AsyncEngine
        """
        from app.config import CONFIG

        if engine := cls.engine_dict.get(sql_alchemy_uri):
            return engine

        engine = create_async_engine(
            sql_alchemy_uri,
            pool_size=CONFIG.ALCHEMY_POLL_SIZE,
            max_overflow=CONFIG.ALCHEMY_OVERFLOW_POOL_SIZE,
            pool_pre_ping=True,
            # echo=True,
        )
        cls.engine_dict[sql_alchemy_uri] = engine
        return engine

    async def get_pg_session(self):
        """Получаем сессию."""
        session_maker = async_sessionmaker(
            self.get_pg_engine(sql_alchemy_uri=self.sql_alchemy_uri),
            expire_on_commit=False,
        )
        async with session_maker() as session:
            yield session

    @asynccontextmanager
    async def get_pg_session_cm(self):
        """Получаем сессию в асинхронном менеджере контекста.

        from app.db.session import connector
        async with connector.get_pg_session_cm() as db:
            obj = await raw_history_crud.create(db=db, obj_in=body)

        """
        session_maker = async_sessionmaker(
            self.get_pg_engine(sql_alchemy_uri=self.sql_alchemy_uri),
            expire_on_commit=False,
        )
        async with session_maker() as session:
            yield session

connector = PGEngineConnector()
