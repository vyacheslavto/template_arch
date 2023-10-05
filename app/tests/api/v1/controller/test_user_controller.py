"""FIXME Тестируем получение сессии. B боевом проекте удалить."""
from secrets import token_hex

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK

from app.api.v1.schemas.http.user_schema import CreateUserSchema
from app.api.v1.schemas.http.user_schema import UserSchema
from app.tests.consts import BASE_URL
from app.tests.utils.sql_init_conts import BASE_INIT_PAYLOAD


@pytest.mark.asyncio
class TestUserController:
    # pytest app/tests/api/v1/controller/test_user_controller.py -rP --tb=native

    stmt = BASE_INIT_PAYLOAD
    URL = f"{BASE_URL}/api/v1/users/"

    async def test_insert_db(self, session: AsyncSession):
        for ins in self.stmt:
            await session.execute(ins)
        await session.commit()

    async def test_create_user(self, client):

        user_name = token_hex(16)
        response = await client.post(
            self.URL,
            json=jsonable_encoder(
                CreateUserSchema(
                    user_name=user_name,
                    role_id=1,
                )
            )
        )
        assert response.status_code == HTTP_200_OK
        assert UserSchema(**response.json()).model_dump(
            exclude={'id', 'created_at', 'updated_at', 'role'}
        ) == {'user_name': user_name}

    async def test_get_all_user(self, client: AsyncClient):
        response = await client.get(url=self.URL)
        assert response.status_code == HTTP_200_OK

        payload = response.json()
        assert len(payload) == 5
