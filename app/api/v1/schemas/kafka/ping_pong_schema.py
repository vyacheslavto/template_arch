from app.api.v1.schemas.base_schema import BaseSchema


class CreatePingPongSchema(BaseSchema):
    ping: int
    pong: int


class PingPongSchema(CreatePingPongSchema):
    id: int
    ping: int
    pong: int
