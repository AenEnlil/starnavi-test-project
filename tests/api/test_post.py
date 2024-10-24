import pytest
import json

from httpx import AsyncClient
from starlette import status

from app.custom_fields import PyObjectId
from app.post.messages import POST_NOT_FOUND
from tests.conftest import POST_DATA


async def test_not_authenticated_user_cant_create_post(client: AsyncClient):
    response = await client.post(url='api/v1/posts/', data=json.dumps(POST_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_read_post(client: AsyncClient):
    post_id = PyObjectId()
    response = await client.get(url=f'api/v1/posts/{post_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_can_create_post(client: AsyncClient, user, token):

    response = await client.post(url='api/v1/posts/',
                                 data=json.dumps(POST_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('title') == POST_DATA.get('title')
    assert response_data.get('text') == POST_DATA.get('text')
    assert response_data.get('user_id') == str(user)


async def test_user_cant_read_not_existing_post(client: AsyncClient, user, token):
    post_id = PyObjectId()
    response = await client.get(url=f'api/v1/posts/{post_id}',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()
    assert response
    assert response.get('detail') == POST_NOT_FOUND


async def test_user_can_read_post(client: AsyncClient, user, token):

    response = await client.post(url='api/v1/posts/',
                                 data=json.dumps(POST_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    created_post = response.json()

    assert created_post
    assert created_post.get('title') == POST_DATA.get('title')
    assert created_post.get('text') == POST_DATA.get('text')
    assert created_post.get('user_id') == str(user)

    post_id = created_post.get('_id')
    response = await client.get(url=f'api/v1/posts/{post_id}',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response
    assert response.get('_id') == post_id
    assert response.get('title') == created_post.get('title')
    assert response.get('text') == created_post.get('text')
    assert response.get('user_id') == str(user)




