"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
import typing as t
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base_class import BaseDBModel

if t.TYPE_CHECKING:
    from app.api.v1.models import UserModel


class UserRoleModel(BaseDBModel):
    """Модель ролей юзера."""

    __tablename__ = "template_user_role"

    id: Mapped[int] = mapped_column(
        primary_key=True, comment="Уникальный идентификатор роли"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        comment="Дата создания роли",
    )
    role_name: Mapped[str] = mapped_column(
        nullable=False, unique=True, comment="Имя роли"  # Уникальный индекс
    )

    users: Mapped[list["UserModel"]] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="role",
        uselist=True,
    )
