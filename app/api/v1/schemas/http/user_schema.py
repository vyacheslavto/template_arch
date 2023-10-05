"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
from datetime import datetime

from pydantic import field_validator

from app.api.v1.schemas.base_schema import BaseSchema
from app.api.v1.schemas.http.role_schema import RoleSchema


class CreateUserSchema(BaseSchema):
    user_name: str
    role_id: int


class UserSchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    user_name: str
    role: RoleSchema

    @field_validator("user_name")
    @classmethod
    def custom_validator(cls, v):
        """Кастомный валидатор имени.

        Args:
        v: value

        Raises:
        ValueError
        """
        assert len(v) > 5, "Кастомная ошибка. Длина имени юзера должна быть больше 5"
        return v
