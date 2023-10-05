import asyncio

import confluent_kafka
from loguru import logger

from app.api.v1.schemas.kafka_schema import KafkaProduceMessageSchema
from app.config import CONFIG
from app.config import Configuration


class BaseAIOKafkaProducer:
    """Базовый асинхронный продюсер кафки."""

    __producer: confluent_kafka.Producer

    def __init__(self):
        """Инициализация продюсера."""
        config = self.config_builder(config=CONFIG)
        self.__producer = confluent_kafka.Producer(config)

    def on_error(self, err, *args, **kwargs):
        """Колбек ошибки продюсера.

        Args:
            err: str - текст ошибки
            *args: аргументы
            **kwargs: кейворд аргументы.
        """
        logger.error(f"Producer error: {err=}, {args=}, {kwargs=}")

    def config_builder(self, config: Configuration) -> dict:
        """Сборщик конфига. Если необходимо, можно отнаследоваться и переопределить.

        Args:
            config: Settings - конфиг приложения.

        Returns:
            dict - конфиг для продюсера
        """
        return {
            "bootstrap.servers": f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
            "logger": logger,
            "error_cb": self.on_error,
            # Можно раскоментировать, если нужны логи o доставке сообщений
            # 'on_delivery': lambda err, msg: logger.info(
            #     f"Доставлено {msg.topic()=} {msg.partition()=} {msg.offset()=}"),
            "message.max.bytes": config.KAFKA_MAX_REQUEST_SIZE,
        }

    async def send_one(self, message: KafkaProduceMessageSchema, topic: str) -> None:
        """Отправка одного сообщения в топик.

        Args:
            message: KafkaProduceMessageSchema - сообщение для отправки
            topic: str - топик для отправки.
        """
        loop = asyncio.get_running_loop()

        self.__producer.produce(
            topic=topic,
            key=message.key,
            headers=message.headers,
            value=message.value.json(),
        )

        await loop.run_in_executor(None, self.__producer.flush)
        logger.debug(f"Отправили сообщение в топик {topic}")

    async def send_many(
        self, messages: list[KafkaProduceMessageSchema], topic: str
    ) -> None:
        """Отправка нескольких сообщений в топик.

        Args:
            messages: list[KafkaProduceMessageSchema] - сообщения для отправки
            topic: str - топик для отправки
        """
        loop = asyncio.get_running_loop()

        for message in messages:
            self.__producer.produce(
                topic=topic,
                key=message.key,
                headers=message.headers,
                value=message.value.json(),
            )

        await loop.run_in_executor(None, self.__producer.flush)
        logger.debug(f"Отправили {len(messages)} сообщений в топик {topic}")
