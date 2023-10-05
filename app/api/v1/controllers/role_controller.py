"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT

from app.api.v1.crud.role_crud import role_crud
from app.api.v1.schemas.base_schema import ErrorSchema
from app.api.v1.schemas.http.role_schema import CreateRoleSchema
from app.api.v1.schemas.http.role_schema import RoleSchema
from app.db.session import connector

router = APIRouter()


@router.get(
    "/",
    response_model=list[RoleSchema],
    description="Получаем все роли, которые есть в таблице user_role",
    summary="Получение всех ролей пользователя",
    responses={
        HTTP_200_OK: {
            "model": list[RoleSchema],  # custom pydantic model for 200 response
            "description": "Список ролей",
        },
    },
)
async def get_all_roles(
    db: AsyncSession = Depends(connector.get_pg_session),
):
    """Получение всех ролей.

    Args:
        db: AsyncSession

    Returns:
        list[RoleSchema]
    """
    return await role_crud.get_multi(db=db)


@router.get(
    "/{role_id}",
    response_model=RoleSchema,
    description="Получение роли по айди, которая лежит в таблице ролей",
    summary="Получение роли по ID",
    responses={
        HTTP_200_OK: {
            "model": RoleSchema,  # custom pydantic model for 200 response
            "description": "Список ролей",
        },
        HTTP_404_NOT_FOUND: {"model": ErrorSchema, "description": "Юзер не найден"},
    },
)
async def get_role_by_id(
    role_id: int,
    db: AsyncSession = Depends(connector.get_pg_session),
):
    """Получаем роль по айди.

    Args:
        role_id: int
        db: AsyncSession

    Returns:
        RoleSchema
    """
    return await role_crud.get(db=db, _id=role_id)


@router.post(
    "/",
    response_model=RoleSchema,
    description="Создание новой роли",
    summary="Создание новой роли",
    responses={
        HTTP_200_OK: {
            "model": RoleSchema,  # custom pydantic model for 200 response
            "description": "Новая роль",
        },
        HTTP_409_CONFLICT: {
            "model": ErrorSchema,  # custom pydantic model for 200 response
            "description": "Роль c таким именем уже существует",
        },
    },
)
async def create_role(
    body: CreateRoleSchema, db: AsyncSession = Depends(connector.get_pg_session)
):
    """Создаем новую роль.

    Args:
        body: CreateRoleSchema
        db: AsyncSession

    Returns:
        RoleSchema
    """
    return await role_crud.create(db=db, obj_in=body)
