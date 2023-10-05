import random

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_405_METHOD_NOT_ALLOWED

from app.tests.consts import BASE_URL


@pytest.mark.usefixtures("client")
class TestHealthCheck:
    URL = f"{BASE_URL}/health/"

    async def test_health_check(self, client: AsyncClient):
        response = await client.get(self.URL)
        assert response.status_code == HTTP_200_OK
        assert response.text == "OK"

    async def test_health_check_fail(self, client: AsyncClient):
        method = random.choice(["POST", "PUT", "DELETE"])
        response = await client.request(method=method, url=self.URL)
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
        assert response.json()["detail"] == "Method Not Allowed"
