import json

import pytest

from httpx import AsyncClient
from starlette import status

from tests.conftest import USER_DATA


async def test_user_login(client: AsyncClient):
    user_data = USER_DATA.copy()
    response = await client.post(url='api/v1/users/', data=json.dumps(user_data))

    assert response.status_code == status.HTTP_201_CREATED

    login_data = json.dumps({'email': user_data.get('email'), 'password': user_data.get('password')})
    response = await client.post(url='api/v1/auth/login', data=login_data)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert response_data
    assert response_data.get('access_token')


async def test_cant_login_with_invalid_credentials(client: AsyncClient):
    user_data = USER_DATA.copy()
    login_data = json.dumps({'email': user_data.get('email'), 'password': user_data.get('password')})
    response = await client.post(url='api/v1/auth/login', data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

