import logging

from fastapi import Request
from loguru import logger


class InterceptHandler(logging.Handler):
    """Отключаем access логи для хелсчека."""

    def emit(self, record):
        """Отклюаем логи для хелсчеков k8s.

        https://segmentfault.com/a/1190000041784538/en

        Args:
            record: объект записи лога
        """
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        if record.getMessage().find("health") == -1:
            logger_opt.log(record.levelname, record.getMessage())


async def log_request_info(request: Request):
    """Логирование запросов c X-HEADERS.

    Args:
        request: Request
    """
    x_headers = []

    for header in request.headers:
        if header.startswith("x-"):
            x_headers.append(header)

    if x_headers:
        logger.info(
            f"{request.method} request to {request.url}" f" with X-HEADERS {x_headers}"
        )
