from unittest.mock import Mock

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.kafka.ping_pong_schema import CreatePingPongSchema
from app.api.v1.workers.ping_pong_worker import PingPongWorker
from app.tests.utils.mocks import MockObject
from app.tests.utils.sql_init_conts import BASE_INIT_PAYLOAD


class TestPingPongWorker:
    ping_pong_worker = PingPongWorker()
    stmt = BASE_INIT_PAYLOAD

    async def test_insert_db(self, session: AsyncSession):
        for ins in self.stmt:
            await session.execute(ins)
        await session.commit()

    async def test_ping_pong_updates(self, monkeypatch):
        async def get_one(*args, **kwargs):
            data = CreatePingPongSchema(
                ping=1,
                pong=2,
            )
            yield MockObject(value=lambda *ag, **kw: data.model_dump_json().encode("utf-8"))

        monkeypatch.setattr(
            "app.api.utils.confluence_kafka_consumer.BaseAIOKafkaConsumer.get_one",
            get_one,
        )
        monkeypatch.setattr(
            "app.api.v1.workers.ping_pong_worker.PingPongWorker." "_save_to_db",
            Mock(side_effect=StopAsyncIteration),
        )

        try:
            await self.ping_pong_worker.run()
        except StopAsyncIteration:
            assert True

    async def test_save_to_db(self, session):
        data = CreatePingPongSchema(ping=1, pong=2)
        obj = await self.ping_pong_worker._create_ping_pong \
            (session=session,
             obj_in=data)

        assert hasattr(obj, "id")
