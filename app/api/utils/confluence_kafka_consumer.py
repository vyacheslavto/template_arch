import asyncio
import functools
from collections.abc import AsyncGenerator
from collections.abc import Sequence

import confluent_kafka
from loguru import logger

from app.config import CONFIG
from app.config import Configuration


class BaseAIOKafkaConsumer:
    """Базовый асинхронный консюмер кафки."""

    __consumer: confluent_kafka.Consumer
    __partition: confluent_kafka.TopicPartition
    topic: str

    def __init__(
            self,
            group_id: str,
            topic: str,
    ):
        """Инициализация консюмера.

        Args:
            group_id: str - группа консюмера
            topic: str - топик, который будем слушать
        """
        self.topic = topic

        config = self.config_builder(config=CONFIG, group_id=group_id)

        self.__consumer = confluent_kafka.Consumer(config)
        self.__consumer.subscribe(
            topics=[topic],
            on_lost=functools.partial(self.on_error_cb, "Соединение до кафки потеряно"),
            on_assign=self.on_assign_cb,
            on_revoke=lambda consumer, partitions: logger.info(
                f"Для {self.topic} отписались от {len(partitions)} партиций"
            ),
        )

        logger.info(f"Инициализировали консьюмер для топика {topic}")

    def on_assign_cb(self, _, partitions):
        """Колбек при подключении к партиции.

        Args:
            _: consumer - не используется
            partitions: TopicPartition - партиция
        """
        self.__partition = partitions
        logger.info(
            f"Для {self.topic} подписались на {len(partitions)} партиций"
        ),

    def on_error_cb(self, err, *args, **kwargs):
        """Колбек ошибки консюмера.

        Args:
            err: str - текст ошибки
            *args: аргументы
            **kwargs: кейворд аргументы
        """
        logger.error(f"Consumer error: {err=}, {args=}, {kwargs=}")

    def config_builder(self, config: Configuration, group_id: str) -> dict:
        """Сборщик конфига. Если необходимо, можно отнаследоваться и переопределить.

        Args:
            config: Settings - конфиг приложения
            group_id: str - группа консюмера

        Returns:
            dict - конфиг для консюмера
        """
        return {
            "bootstrap.servers": f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
            "group.id": group_id,
            "error_cb": self.on_error_cb,
            "logger": logger,
            "heartbeat.interval.ms": config.KAFKA_HEARTBEAT_INTERVAL_MS,
            "session.timeout.ms": config.KAFKA_SESSION_TIMEOUT_MS,
            "message.max.bytes": config.KAFKA_MAX_REQUEST_SIZE,
        }

    async def send_heartbeat(self):
        """Отправляем хертбит до кафки.

        При паузе потребления метод pool всегда будет
        возвращать None вместо сообщения, заодно отправив хертбит.
        https://stackoverflow.com/a/54768466.

        """
        loop = asyncio.get_running_loop()
        self.__consumer.pause(self.__partition)
        await loop.run_in_executor(None, self.__consumer.poll, 0.1)
        self.__consumer.resume(self.__partition)

    async def get_many(
            self,
    ) -> AsyncGenerator[Sequence[confluent_kafka.Message], None]:
        """Получение нескольких сообщений из кафки."""
        loop = asyncio.get_running_loop()

        try:
            while True:
                messages = await loop.run_in_executor(
                    None,
                    self.__consumer.consume,
                    CONFIG.KAFKA_DEFAULT_BULK_SIZE,  # num_messages
                    CONFIG.KAFKA_DEFAULT_BULK_TIMEOUT,
                )  # timeout

                if messages is None:
                    await asyncio.sleep(1)
                    continue

                yield messages

        except (KeyboardInterrupt, SystemExit):
            self.__consumer.close()

        finally:
            self.__consumer.close()

    async def get_one(self) -> AsyncGenerator[confluent_kafka.Message, None]:
        """Получение одного сообщения из кафки."""
        loop = asyncio.get_running_loop()
        logger.info(f"Запустили потребление топика {self.topic} по одному сообщению")
        try:
            while True:
                message = await loop.run_in_executor(None, self.__consumer.poll, 0.1)
                if message is None:
                    await asyncio.sleep(0.1)
                    continue

                if message.error():
                    continue

                yield message

        except (KeyboardInterrupt, SystemExit):
            self.__consumer.close()
        finally:
            self.__consumer.close()
