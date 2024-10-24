import json

import pytest

from httpx import AsyncClient
from starlette import status

from tests.conftest import USER_DATA, POST_DATA


async def test_unauthorized_user_cant_create_post(client: AsyncClient):
    response = await client.post(url='api/v1/posts/', data=json.dumps(POST_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_can_create_post(client: AsyncClient, user, token):

    response = await client.post(url='api/v1/posts/',
                                 data=json.dumps(POST_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('text') == POST_DATA.get('text')
    assert response_data.get('user_id') == str(user)





