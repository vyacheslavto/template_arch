import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(cwd)
sys.path.append(parent)

import asyncio
import uuid

from loguru import logger

from app.api.utils.confluence_kafka_producer import BaseAIOKafkaProducer
from app.api.v1.schemas.kafka.ping_pong_schema import CreatePingPongSchema
from app.api.v1.schemas.kafka_schema import KafkaProduceMessageSchema


async def ping_pong_produce():
    from app.config import CONFIG

    # python cli.py cli.produce "ping_pong_produce()"

    producer = BaseAIOKafkaProducer()
    headers = {
        "x-request-id": str(uuid.uuid4()),
    }

    payload = {"ping": 13, "pong": 13}

    message = KafkaProduceMessageSchema(
        headers=headers, value=CreatePingPongSchema(**payload)
    )
    await producer.send_one(message=message, topic=CONFIG.KAFKA_PING_PONG_TOPIC)
    logger.opt(colors=True).info(
        f"<yellow>{CONFIG.KAFKA_PING_PONG_TOPIC}</yellow> [ <green> {payload} </green> ]"
    )


if __name__ == "__main__":
    # Запуск через точки остановки (просто нажать ▶️)

    asyncio.run(ping_pong_produce())
