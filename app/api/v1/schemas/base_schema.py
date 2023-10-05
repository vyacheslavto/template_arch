"""Базовая схема ORJSON, которую можно использовать как базовую pydantic схему."""

from pydantic import BaseModel
from pydantic import ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        from_attributes=True
    )

class ErrorSchema(BaseSchema):
    detail: str
