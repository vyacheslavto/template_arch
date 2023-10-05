import asyncio
import os
import platform

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.utils.enums.env_enum import EnvEnum
from app.db.base_class import BaseDBModel
from app.db.session import PGEngineConnector
from app.main import get_fastapi_app

# Нужно явно указать для тестирования миграций
os.environ["ENVIRONMENT"] = EnvEnum.PYTEST.value


def get_test_sql_alchemy_uri():
    from app.config import CONFIG

    return CONFIG.TEST_SQLALCHEMY_DATABASE_URI


def get_test_connector():
    return PGEngineConnector(sql_alchemy_uri=get_test_sql_alchemy_uri())


@pytest.fixture(scope="session")
def event_loop():
    """Фикстура для получения евент лупа.
    Проверяем, закрыт ли луп, и запущен ли он на винде.
    """
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    """Фикстура для получения движка алхимии.
    Используется для наката / отката состояния бд.
    """
    connector = get_test_connector()
    engine = connector.get_pg_engine(sql_alchemy_uri=get_test_sql_alchemy_uri())
    yield engine
    await engine.dispose()


@pytest.fixture(scope="class")
async def db_init(engine):
    """Фикстура для скидывания состояния БД.

    Args:
        engine: AsyncEngine
    """
    meta = BaseDBModel.metadata

    async with engine.connect() as conn:
        # FIXME Если нужны тесты c выкладкой на тестовую БД, то указать явно схему,
        #  которую нужно пересоздать

        await conn.execute(text("DROP SCHEMA IF EXISTS template_schema CASCADE;"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS template_schema;"))

        await conn.run_sync(meta.create_all)
        await conn.commit()


@pytest.fixture(scope="class")
async def migrations_clean_up(engine):
    """Фикстура для тестирования миграций.
    Главное отличие от session фикстуры - нет conn.run_sync(meta.create_all).

    Args:
        engine: AsyncEngine
    """
    async with engine.begin() as conn:
        # FIXME указать, какую схему стоит пересоздать.
        #  Используется для тестирования миграции.

        await conn.execute(text("DROP SCHEMA IF EXISTS template_schema CASCADE;"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS template_schema;"))


@pytest.fixture(scope="class")
async def session(engine, db_init):
    session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    """Yields:
    c (TestClient): Экземпляр клиента.
    """
    from app.db.session import connector

    main_app = get_fastapi_app()
    test_connector = get_test_connector()

    main_app.dependency_overrides[
        connector.get_pg_session
    ] = test_connector.get_pg_session

    async with AsyncClient(app=main_app, follow_redirects=True) as client:
        yield client
