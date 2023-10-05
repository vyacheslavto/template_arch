"""Сюда импортируем все модели, которые должны использоваться в миграциях."""
from app.api.v1.models import *  # noqa
from app.db.base_class import BaseDBModel  # noqa
