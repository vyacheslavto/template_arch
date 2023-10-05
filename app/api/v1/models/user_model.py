"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
import typing as t
from datetime import UTC
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.annotated_fields import dt_utcnow
from app.db.base_class import BaseDBModel

if t.TYPE_CHECKING:
    from app.api.v1.models import UserRoleModel


class UserModel(BaseDBModel):
    """https://github.com/zhanymkanov/fastapi-best-practices#13-set-db-naming-convention.

    При нейминге моделей следуем этому правилу
    - snake_case
    - единственное число
    - группировать имя в модулях начиная c имя модуля, например
    template_user, template_books, payments_user
    - Придерживаемся единообразия в таблицах
    - _at суффикс для datetime
    - _date суффикс для date.

    """

    __tablename__ = "template_user"

    id: Mapped[int] = mapped_column(
        primary_key=True, comment="Уникальный идентификатор юзера"
    )
    created_at: Mapped[dt_utcnow] = mapped_column(
        nullable=False,
        server_default=func.now(),
        comment="Дата создания юзера",
    )
    updated_at: Mapped[dt_utcnow] = mapped_column(
        nullable=False,
        server_onupdate=func.now(),  # Автоматически обновляем дату изменения
        default=datetime.now(tz=UTC),
        comment="Дата обновления юзера",
    )
    user_name: Mapped[str] = mapped_column(
        nullable=False, unique=True, comment="Имя юзера"  # Уникальный индекс
    )
    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("template_schema.template_user_role.id", ondelete="SET NULL"),
        nullable=True,
        server_default=text("1"),
        comment="ФК на роль",
    )
    role: Mapped["UserRoleModel"] = relationship(
        back_populates="users", lazy="selectin"
    )
