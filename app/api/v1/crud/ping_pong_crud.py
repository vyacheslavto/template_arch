"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
from app.api.v1.crud.base_crud import BaseCRUD
from app.api.v1.models import PingPongModel


class PingPongCRUD(BaseCRUD):
    pass


ping_pong_crud = PingPongCRUD(PingPongModel)
