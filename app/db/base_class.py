from typing import Any

from sqlalchemy.orm import DeclarativeBase


class BaseDBModel(DeclarativeBase):
    __tablename__: Any
    __table_args__ = {"schema": "template_schema"}

    @classmethod
    def group_by_fields(cls, exclude: list[str] | None = None):
        """Берем имена всех колонок для группировки.

        Args:
            exclude: list[str] | None исключаемые поля

        Returns:
            list[колонка]
        """
        payload = []
        if not exclude:
            exclude = []

        for column in cls.__table__.columns:
            if column.key in exclude:
                continue

            payload.append(column)
        return payload

    @classmethod
    def jsonb_build_object(cls, exclude: list[str] | None = None):
        """Build jsonb object для модели.

        Args:
            exclude: Исключаемые поля.

        Returns:
            list[ключ колонки, колонка
        """
        payload = []

        if not exclude:
            exclude = []

        for column in cls.__table__.columns:
            if column.key in exclude:
                continue

            payload.append(column.key)
            payload.append(column)
        return payload
