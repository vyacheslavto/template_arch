"""FIXME Тестируем получение сессии. B боевом проекте удалить."""
import pytest
from sqlalchemy.sql import text

from app.config import CONFIG
from app.db.session import PGEngineConnector


@pytest.mark.asyncio
class TestPGEngineSingleton:
    connector = PGEngineConnector(sql_alchemy_uri=CONFIG.TEST_SQLALCHEMY_DATABASE_URI)

    async def test_get_pg_engine(self):
        engine = self.connector.get_pg_engine(
            sql_alchemy_uri=CONFIG.TEST_SQLALCHEMY_DATABASE_URI
        )
        second_engine = self.connector.get_pg_engine(
            sql_alchemy_uri=CONFIG.TEST_SQLALCHEMY_DATABASE_URI
        )

        assert engine == second_engine

        other_engine = self.connector.get_pg_engine(
            sql_alchemy_uri="postgresql+asyncpg://localhost"
        )

        assert engine != other_engine

    async def test_get_pg_session(self):
        session = self.connector.get_pg_session()
        second_session = self.connector.get_pg_session()

        assert session != second_session
        assert type(session) == type(second_session)

    async def test_select_one(self):
        session = self.connector.get_pg_session()

        async for s in session:
            data = await s.execute(text("SELECT 1"))
            payload = data.scalars().first()
            assert payload == 1
