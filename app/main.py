import asyncio
import logging
import sys
import time
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api import router
from app.api.utils.enums.env_enum import EnvEnum
from app.api.utils.loggers import InterceptHandler
from app.api.v1.workers.ping_pong_worker import PingPongWorker
from app.config import CONFIG


def get_fastapi_app() -> FastAPI:
    """Получаем объект фастапи c прогруженными роутами.

    Returns:
        FastAPI
    """
    fast_api_app = FastAPI(
        default_response_class=ORJSONResponse,
        title=CONFIG.PROJECT_NAME,
        openapi_url="/openapi.json",
    )
    fast_api_app.include_router(router)
    return fast_api_app


app = get_fastapi_app()

# Set all CORS enabled origins
if CONFIG.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in CONFIG.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Response:
    """Добавление времени выполнения сервиса в ответ.

    Args:
        request (Request): Объект запроса
        call_next (Any): Функция которая получит request в качестве параметра.

    Returns:
        Response: Объект ответа приложения
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def init_logger():
    """Метод инициализации логеров."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message} in {name} {line}",
        level="INFO"
        if CONFIG.ENVIRONMENT in [EnvEnum.DEV, EnvEnum.TEST, EnvEnum.PROD]
        else "DEBUG",
    )
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message} in {name} {line}",
        level="ERROR",
    )
    logging.getLogger("uvicorn.access").setLevel(10)
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").addHandler(InterceptHandler())


@app.on_event("startup")
async def startup_kafka_worker():
    """Запускаем kafka workers в EventLoop."""
    if not CONFIG.KAFKA_WORKERS_ENABLED:
        logger.info(f"Потребление кафки отключено, {CONFIG.KAFKA_WORKERS_ENABLED=}")
        return

    loop = asyncio.get_running_loop()

    # workers
    ping_pong_worker = PingPongWorker()
    loop.create_task(ping_pong_worker.run())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
