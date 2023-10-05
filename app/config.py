from typing import Any

from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pydantic import PostgresDsn
from pydantic import ValidationError
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from app.api.utils.enums.env_enum import EnvEnum
from app.api.utils.enums.log_level_enum import LogLevelEnum


class Configuration(BaseSettings):
    """Класс конфигурации. Содержит все переменные, которые мы используем в проекте."""

    def __init__(self, **values: Any):
        load_dotenv(find_dotenv())
        super().__init__(**values)

    @model_validator(mode="before")
    @classmethod
    def assemble_db_connection(cls, data: Any) -> dict:
        """Собираем PG-URI."""
        sqlalchemy_db_uri = None
        if data.get("POSTGRES_USER") and data.get("POSTGRES_HOST"):
            sqlalchemy_db_uri = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=data.get("POSTGRES_USER"),
                password=data.get("POSTGRES_PASSWORD"),
                host=data.get("POSTGRES_HOST"),
                port=int(data.get("POSTGRES_PORT", 5432)),
                path=data.get('POSTGRES_DB', "")
            )

        if not sqlalchemy_db_uri:
            raise ValidationError(
                "Please fill Postgres settings in ENV"
            )
        data.update({"SQLALCHEMY_DATABASE_URI": str(sqlalchemy_db_uri)})
        return data

    @model_validator(mode="before")
    @classmethod
    def assemble_cors_origin(cls, data: Any) -> dict:
        """Валидируем корсы."""
        backend_cors_origins = data.get("BACKEND_CORS_ORIGINS")
        if backend_cors_origins:
            if isinstance(backend_cors_origins, str)\
                and not backend_cors_origins.startswith("["):
                backend_cors_origins = [i.strip()
                for i in backend_cors_origins.split(",")]
            elif isinstance(backend_cors_origins, list | str):
                pass
            else:
                raise ValueError(
                    f"BACKEND_CORS_ORIGINS={backend_cors_origins} validation error"
                )
            data.update({"BACKEND_CORS_ORIGINS": backend_cors_origins})
        return data

    ENVIRONMENT: EnvEnum
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.INFO

    # FIXME если не нужны корсы, удалить
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    # FIXME имя проекта.
    PROJECT_NAME: str = "template_service"

    # FIXME postgres. Если не используется - удалить.
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int | str = 5432  # пайпа гитлаба упадет, т.к. прокидывается стринг
    POSTGRES_USER: str | None = "user"
    POSTGRES_PASSWORD: str | None = ""
    POSTGRES_DB: str | None = ""
    SQLALCHEMY_DATABASE_URI: str | None
    TEST_SQLALCHEMY_DATABASE_URI: str | None = ""
    ALCHEMY_POLL_SIZE: int = 10  # Размер пула соединений алхимии
    ALCHEMY_OVERFLOW_POOL_SIZE: int = 20  # Размер очереди соединений

    # FIXME kafka. Если не используется - удалить.
    KAFKA_HOST: str = "localhost"
    KAFKA_PORT: int = 9094
    KAFKA_HEARTBEAT_INTERVAL_MS: int = 3_000
    KAFKA_SESSION_TIMEOUT_MS: int = 15_000
    KAFKA_MAX_REQUEST_SIZE: int = 1048576  # 1 мегабайт
    KAFKA_DEFAULT_BULK_SIZE: int = 100
    KAFKA_DEFAULT_BULK_TIMEOUT: int = 1
    KAFKA_WORKERS_ENABLED: bool = True

    # FIXME kafka topics. Если не используется - удалить.
    KAFKA_PING_PONG_TOPIC: str = "ping_pong"

    # FIXME kafka consumers groups. Если не используется - удалить.
    KAFKA_PING_PONG_CONSUMER_GROUP: str = f"{PROJECT_NAME}__consumer"


    model_config = SettingsConfigDict(case_sensitive=True)


CONFIG = Configuration()
