"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base_class import BaseDBModel


class PingPongModel(BaseDBModel):
    """Тестовая модель для топика ping_pong."""

    __tablename__ = "template_ping_pong"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    ping: Mapped[int] = mapped_column(
        nullable=False,
    )
    pong: Mapped[int] = mapped_column(
        nullable=False,
    )
