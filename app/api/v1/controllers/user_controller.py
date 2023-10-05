"""FIXME Сделано в демонстрационных целях. Удалить в боевом проекте."""
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT

from app.api.v1.crud.user_crud import user_crud
from app.api.v1.schemas.base_schema import ErrorSchema
from app.api.v1.schemas.http.user_schema import CreateUserSchema
from app.api.v1.schemas.http.user_schema import UserSchema
from app.db.session import connector

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserSchema],
    description="Получаем всех юзеров и ролей к ним",
    summary="Получение всех юзеров",
    responses={
        HTTP_200_OK: {
            "model": list[UserSchema],  # custom pydantic model for 200 response
            "description": "Список пользователей",
        },
    },
)
async def get_all_users(
    db: AsyncSession = Depends(connector.get_pg_session),
):
    """Получение всех ролей."""
    return await user_crud.get_multi(db=db)


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    description="Получение юзера по айди",
    summary="Получение юзера по айди",
    responses={
        HTTP_200_OK: {
            "model": UserSchema,
            "description": "Список юзеров",
        },
        HTTP_404_NOT_FOUND: {"model": ErrorSchema, "description": "Юзер не найден"},
    },
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(connector.get_pg_session),
):
    """Получаем роль по айди.

    Args:
        user_id: int
        db: AsyncSession

    Returns:
        RoleSchema
    """
    return await user_crud.get(db=db, _id=user_id)


@router.post(
    "/",
    response_model=UserSchema,
    description="Создание нового юзера",
    summary="Создание нового юзера",
    responses={
        HTTP_200_OK: {
            "model": UserSchema,  # custom pydantic model for 200 response
            "description": "Новый юзер",
        },
        HTTP_409_CONFLICT: {
            "model": ErrorSchema,
            "description": "Юзер c таким именем уже существует, "
            "либо переданной role_id нет в базе",
        },
    },
)
async def create_user(
    body: CreateUserSchema, db: AsyncSession = Depends(connector.get_pg_session)
):
    """Создаем юзера.

    Args:
        body: CreateUserSchema
        db: AsyncSession

    Returns:
        UserSchema
    """
    return await user_crud.create(db=db, obj_in=body)


@router.delete(
    "/{user_id}",
    status_code=HTTP_204_NO_CONTENT,
    description="Удаление юзера",
    summary="Удаление юзера",
)
async def delete_user(
    user_id: int, db: AsyncSession = Depends(connector.get_pg_session)
):
    """Удаляем юзера.

    Args:
        user_id: int
        db: AsyncSession

    Returns:
        UserSchema
    """
    await user_crud.remove(db=db, _id=user_id)
