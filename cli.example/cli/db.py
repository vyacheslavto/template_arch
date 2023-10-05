import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(cwd)
sys.path.append(parent)

import asyncio
import pprint
import uuid
from collections.abc import AsyncGenerator

from loguru import logger
from simple_print import sprint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.v1.crud.ping_pong_crud import ping_pong_crud
from app.api.v1.crud.role_crud import role_crud
from app.api.v1.schemas.http import role_schema
from app.api.v1.schemas.kafka import ping_pong_schema
from app.config import CONFIG

async_engine = create_async_engine(
    CONFIG.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=False,
    # echo=True
)


async_session = async_sessionmaker(async_engine, expire_on_commit=False)


# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_role():
    # python cli.py cli.db "create_role()"

    async with async_session() as db:
        for _ in range(15):
            obj_in = {"role_name": str(uuid.uuid4())[:8]}
            body = role_schema.CreateRoleSchema(**obj_in)
            obj = await role_crud.create(db=db, obj_in=body)

    # Можно принтить удобным для Bac инструментом
    sprint(obj.id)
    pprint.pprint(obj.__dict__)
    logger.info(obj.id)

    logger.opt(colors=True).info("<yellow>create_role</yellow> [ <green> OK </green> ]")


async def get_role():
    # python cli.py cli.db "get_role()"

    async with async_session() as db:
        obj = await role_crud.get(db=db, _id=1)

    sprint(obj.id)
    pprint.pprint(obj.__dict__)
    logger.info(obj.id)

    logger.opt(colors=True).info("<yellow>get_role</yellow> [ <green> OK </green> ]")


async def create_ping_pong():
    # python cli.py cli.db "create_ping_pong()"

    obj_in = {"ping": 1, "pong": 1}
    body = ping_pong_schema.CreatePingPongSchema(**obj_in)

    async with async_session() as db:
        obj = await ping_pong_crud.create(db=db, obj_in=body)

    sprint(obj.id)
    pprint.pprint(obj.__dict__)
    logger.info(obj.id)

    logger.opt(colors=True).info(
        "<yellow>create_ping_pong</yellow> [ <green> OK </green> ]"
    )


if __name__ == "__main__":
    # Запуск через точки остановки (просто нажать ▶️)

    asyncio.run(create_role())
