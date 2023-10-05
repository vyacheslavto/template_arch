from typing import Any

from app.api.v1.schemas.base_schema import BaseSchema


class KafkaProduceMessageSchema(BaseSchema):
    value: BaseSchema
    key: str | None = None
    headers: dict[str, Any] | None = None
