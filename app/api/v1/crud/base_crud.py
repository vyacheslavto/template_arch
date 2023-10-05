from collections.abc import Sequence
from typing import Any
from typing import Generic
from typing import TypeVar

from asyncpg import ForeignKeyViolationError
from asyncpg import UniqueViolationError
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Row
from sqlalchemy import RowMapping
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.db.base_class import BaseDBModel

ModelType = TypeVar("ModelType", bound=BaseDBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    @property
    def now(self):
        """Текущее время в UTC на уровне БД.

        Returns:
            func.timezone: текущее время в UTC на уровне БД.
        """
        return func.timezone("utc", func.now())

    async def get(self, db: AsyncSession, _id: Any) -> Row | RowMapping:
        """Получаем элемент по айди.

        Args:
            db: AsyncSession
            _id: Any

        Returns:
            Row | RowMapping

        Raises:
            HTTPException
        """
        if _id > 2 ** 31:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Переданы слишком большие интовые числа {_id}",
            )

        stmt = await db.execute(select(self.model).where(self.model.id == _id))
        data = stmt.scalars().first()

        if not data:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="He найдено!")
        return data

    async def get_multi(
            self, db: AsyncSession, *, skip: int | None = None, limit: int | None = None
    ) -> Sequence[Row | RowMapping | Any]:
        """Получаем множество элементов c пагинацией.

        Args:
            db: AsyncSession
            skip: int - оффсет
            limit: int - ограничение выборки

        Returns:
            Sequence[Row | RowMapping | Any]
        """
        stmt = select(self.model)

        if limit:
            stmt = stmt.limit(limit)
        if skip:
            stmt = stmt.offset(skip)

        data = await db.execute(stmt)
        return data.scalars().all()

    async def create(
            self, db: AsyncSession, *, obj_in: CreateSchemaType,
            exclude: set | None = None
    ) -> Row | RowMapping:
        """Создаем запись в БД.

        Args:
            db: AsyncSession
            obj_in: CreateSchemaType
            exclude: set - исключаемые поля

        Returns:
             Row | RowMapping

        Raises:
            HTTPException
        """
        obj_in_data = jsonable_encoder(obj_in, exclude_none=True, exclude=exclude)
        try:
            db_object = await db.execute(insert(self.model).values(**obj_in_data))
            await db.commit()
            refresh_object = await self.get(
                db=db, _id=db_object.inserted_primary_key[0]
            )
            return refresh_object

        except IntegrityError as e:
            match e.orig.sqlstate:
                case UniqueViolationError.sqlstate:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail=f"Поля переданные в модель {self.model} содержат "
                               f"неуникальные значения",
                    ) from e
                case ForeignKeyViolationError.sqlstate:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail="Вы пытаетесь связать поля c "
                               "несуществующими значениями FK",
                    ) from e
                case _:
                    raise HTTPException(
                        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=str(e.orig),
                    ) from e

    async def update(
            self, db: AsyncSession, *, _id: int,
            obj_in: UpdateSchemaType
    ) -> Row | RowMapping:
        """Обновляем запись по айди.

        Args:
            db: AsyncSession
            _id: int - айди поля
            obj_in: - схема c данными для обновления

        Returns:
            Row | RowMapping

        Raises:
            HTTPException
        """
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == _id)
                .values(**obj_in.dict(exclude_unset=True))
                .returning(self.model)
            )
            payload = await db.execute(stmt)
            await db.commit()
            return payload.scalars().first()

        except IntegrityError as e:
            match e.orig.sqlstate:
                case ForeignKeyViolationError.sqlstate:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail="Вы пытаетесь прикрепить foreign key к таблице, "
                               "в которой нет такого id",
                    ) from e
                case UniqueViolationError.sqlstate:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail=f"Поля переданные в модель {self.model} содержат "
                               f"неуникальные значения",
                    ) from e
                case _:
                    raise HTTPException(
                        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=str(e),
                    ) from e

    async def remove(self, db: AsyncSession, *, _id: int) -> None:
        """Удаляем объект по айди.

        Args:
            db: AsyncSession
            _id: int - айди сущности в БД
        """
        await db.execute(delete(self.model).where(self.model.id == _id))
        await db.commit()
