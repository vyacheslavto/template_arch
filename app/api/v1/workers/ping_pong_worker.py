from loguru import logger
from pydantic import ValidationError
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.api.utils.confluence_kafka_consumer import BaseAIOKafkaConsumer
from app.api.v1.crud.ping_pong_crud import ping_pong_crud
from app.api.v1.schemas.kafka.ping_pong_schema import CreatePingPongSchema
from app.api.v1.workers.abstract_worker import AbstractWorker
from app.config import CONFIG
from app.db.session import connector


class PingPongWorker(AbstractWorker):
    def __init__(self):
        self.topic = CONFIG.KAFKA_PING_PONG_TOPIC
        self.consumer = BaseAIOKafkaConsumer(
            topic=self.topic,
            group_id=CONFIG.KAFKA_PING_PONG_TOPIC,
        )

    async def run(self):
        """Метод запуска воркера в бекграунде."""
        async for message in self.consumer.get_one():
            logger.opt(colors=True).info(
                f"Получили сообщение {message}"
                f"topic={self.topic} <green>[  OK  ]</green>"
            )
            try:
                validated_message = CreatePingPongSchema.\
                    model_validate_json(message.value())
                if validated_message:
                    obj = await self._save_to_db(data=validated_message)
                    logger.opt(colors=True).info(
                        f"Сохранили сообщение в базу данных; "
                        f"<green>модель {obj.__class__.__name__} id={obj.id}</green>; "
                        f"<blue>топик {self.topic}</blue>"
                    )
            except ValidationError as e:
                logger.error(
                    f"He смогли отвалидировать сообщение.\n"
                    f"topic = {self.topic} offset = {message.offset}\n"
                    f"{e}"
                )
                continue

    @staticmethod
    async def _create_ping_pong(session: AsyncSession,
                                obj_in: CreatePingPongSchema):
        return await ping_pong_crud.create(db=session, obj_in=obj_in)

    @staticmethod
    async def _save_to_db(data: CreatePingPongSchema) -> Row | None:
        try:
            async for db in connector.get_pg_session():
                return await PingPongWorker._create_ping_pong(
                    session=db,
                    obj_in=data
                )
        except HTTPException as e:
            logger.info(e.detail)
        return None
