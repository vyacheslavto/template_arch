import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(cwd)
sys.path.append(parent)

import asyncio

from loguru import logger
from simple_print import sprint


async def hello_stranger():
    # python cli.py cli.hello "hello_stranger()"
    # запуск через cli.py

    logger.opt(colors=True).info(
        "<yellow>War...</yellow> <green>War never changes ☢️</green>"
    )
    sprint(
        "The end of the world occurred pretty much as we had predicted", c="blue", p=1
    )


if __name__ == "__main__":
    # Запуск через точки остановки (просто нажать ▶️)

    asyncio.run(hello_stranger())
