"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
from datetime import datetime

from app.api.v1.schemas.base_schema import BaseSchema


class CreateRoleSchema(BaseSchema):
    role_name: str


class RoleSchema(BaseSchema):
    id: int
    role_name: str
    created_at: datetime
