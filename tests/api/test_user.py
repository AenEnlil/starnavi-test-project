import pytest
import json

from httpx import AsyncClient
from starlette import status

from app.messages import USER_SETTINGS_READ_NOT_ALLOWED, USER_SETTINGS_UPDATE_NOT_ALLOWED
from tests.conftest import USER_DATA, USER_SETTINGS


async def test_user_register(client: AsyncClient):
    response = await client.post(url='api/v1/users/', data=json.dumps(USER_DATA.copy()))

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('email') == USER_DATA.get('email')


async def test_not_authenticated_user_cant_read_settings(client: AsyncClient, user):
    response = await client.get(url=f'api/v1/users/{user}/settings')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_edit_settings(client: AsyncClient, user):
    response = await client.patch(url=f'api/v1/users/{user}/settings',
                                  data=json.dumps(USER_SETTINGS.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_cant_read_someone_else_settings(client: AsyncClient, user, token, user2):
    response = await client.get(url=f'api/v1/users/{user2}/settings',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()

    assert response
    assert response.get('detail') == USER_SETTINGS_READ_NOT_ALLOWED


async def test_user_cant_edit_someone_else_settings(client: AsyncClient, user, token, user2):
    response = await client.patch(url=f'api/v1/users/{user2}/settings',
                                  data=json.dumps(USER_SETTINGS.copy()),
                                  headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()

    assert response
    assert response.get('detail') == USER_SETTINGS_UPDATE_NOT_ALLOWED


async def test_user_can_read_his_settings(client: AsyncClient, user, token):
    response = await client.get(url=f'api/v1/users/{user}/settings',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response
    assert response.get('automatic_response_enabled') is False
    assert response.get('automatic_response_delay_in_minutes') == 15


async def test_user_can_edit_his_settings(client: AsyncClient, user, token):
    response = await client.get(url=f'api/v1/users/{user}/settings',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    old_settings = response.json()
    new_settings = USER_SETTINGS.copy()

    assert old_settings.get('automatic_response_enabled') != new_settings.get('automatic_response_enabled')
    assert old_settings.get('automatic_response_delay_in_minutes') != new_settings.get('automatic_response_delay_in_minutes')

    response = await client.patch(url=f'api/v1/users/{user}/settings',
                                  data=json.dumps(new_settings),
                                  headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response
    assert response.get('automatic_response_enabled') == new_settings.get('automatic_response_enabled')
    assert response.get('automatic_response_delay_in_minutes') == new_settings.get('automatic_response_delay_in_minutes')
