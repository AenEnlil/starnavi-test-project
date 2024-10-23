import json

import pytest

from httpx import AsyncClient
from starlette import status

from tests.conftest import USER_DATA


async def test_user_register(client: AsyncClient):
    response = await client.post(url='api/v1/users/', data=json.dumps(USER_DATA.copy()))

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('email') == USER_DATA.get('email')
