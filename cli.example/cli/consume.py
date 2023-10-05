import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(cwd)
sys.path.append(parent)

import asyncio

from app.api.v1.workers.ping_pong_worker import PingPongWorker


async def ping_pong_consume():
    # python cli.py cli.consume "ping_pong_consume()"

    ping_pong_worker = PingPongWorker()
    await ping_pong_worker.run()


if __name__ == "__main__":
    # Запуск через точки остановки (просто нажать ▶️)

    asyncio.run(ping_pong_consume())
