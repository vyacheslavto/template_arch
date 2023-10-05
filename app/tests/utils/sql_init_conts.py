"""Файл для констант c инстертами в БД."""
from typing import Any

from sqlalchemy import insert

from app.api.v1.models import UserModel
from app.api.v1.models import UserRoleModel

BASE_INIT_PAYLOAD: list[Any] = [
    insert(UserRoleModel).values(
        [
            dict(role_name="some_role"),
            dict(role_name="some_role2"),
            dict(role_name="some_role3"),
            dict(role_name="some_role4"),
        ]
    ),
    insert(UserModel).values(
        [
            dict(user_name="some_user_name"),
            dict(user_name="some_user_name2"),
            dict(user_name="some_user_name3"),
            dict(user_name="some_user_name4"),
        ]
    ),
]
