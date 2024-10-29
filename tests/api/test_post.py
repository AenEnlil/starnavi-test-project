import pytest
import json

from httpx import AsyncClient
from starlette import status

from app.custom_fields import PyObjectId
from app.database import get_comment_collection
from app.messages import POST_NOT_FOUND, POST_EDIT_NOT_ALLOWED, POST_DELETE_NOT_ALLOWED, POST_ALREADY_EXISTS
from tests.conftest import POST_DATA


async def test_not_authenticated_user_cant_create_post(client: AsyncClient):
    response = await client.post(url='api/v1/posts/', data=json.dumps(POST_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_read_post(client: AsyncClient):
    post_id = PyObjectId()
    response = await client.get(url=f'api/v1/posts/{post_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_get_post_list(client: AsyncClient):
    response = await client.get(url=f'api/v1/posts/')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_edit_post(client: AsyncClient):
    post_id = PyObjectId()
    response = await client.patch(url=f'api/v1/posts/{post_id}', data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_delete_post(client: AsyncClient):
    post_id = PyObjectId()
    response = await client.delete(url=f'api/v1/posts/{post_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_cant_create_post_with_same_title_if_he_already_created_one(client: AsyncClient, user, token):
    response = await client.post(url='api/v1/posts/',
                                 data=json.dumps(POST_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('title') == POST_DATA.get('title')
    assert response_data.get('text') == POST_DATA.get('text')
    assert response_data.get('user_id') == str(user)

    response = await client.post(url='api/v1/posts/',
                                 data=json.dumps(POST_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()
    assert response
    assert response.get('detail') == POST_ALREADY_EXISTS


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


async def test_user_cant_edit_not_existing_post(client: AsyncClient, user, token):
    post_id = PyObjectId()
    new_data = {'title': 'New Title'}
    response = await client.patch(url=f'api/v1/posts/{post_id}',
                                  data=json.dumps(new_data),
                                  headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = response.json()
    assert response
    assert response.get('detail') == POST_NOT_FOUND


async def test_user_cant_edit_someone_else_post(client: AsyncClient, user, token, user2, token2):
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
    new_data = {'title': 'New Title', 'random_field': 123}
    response = await client.patch(url=f'api/v1/posts/{post_id}',
                                  data=json.dumps(new_data),
                                  headers={'Authorization': f'Bearer {token2}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()

    assert response
    assert response.get('detail') == POST_EDIT_NOT_ALLOWED


async def test_user_can_edit_post(client: AsyncClient, user, token):

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
    new_data = {'title': 'New Title', 'random_field': 123}
    response = await client.patch(url=f'api/v1/posts/{post_id}',
                                  data=json.dumps(new_data),
                                  headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response
    assert response.get('_id') == post_id
    assert response.get('title') == new_data.get('title')
    assert not response.get('random_field')


async def test_user_cant_delete_not_existing_post(client: AsyncClient, user, token):
    post_id = PyObjectId()
    response = await client.delete(url=f'api/v1/posts/{post_id}',
                                   headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = response.json()
    assert response
    assert response.get('detail') == POST_NOT_FOUND


async def test_user_cant_delete_someone_else_post(client: AsyncClient, user, token, user2, token2):
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
    response = await client.delete(url=f'api/v1/posts/{post_id}',
                                   headers={'Authorization': f'Bearer {token2}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()

    assert response
    assert response.get('detail') == POST_DELETE_NOT_ALLOWED


async def test_user_can_delete_post(client: AsyncClient, user, token):

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
    response = await client.delete(url=f'api/v1/posts/{post_id}',
                                   headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response
    assert response.get('deleted')


async def test_when_user_delete_post_all_related_comment_deleted(client: AsyncClient, user, token, post, comment,
                                                                 comment2):
    comments_count = get_comment_collection().count_documents({'post_id': post})
    assert comments_count == 2

    response = await client.delete(url=f'api/v1/posts/{post}',
                                   headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response = response.json()

    assert response
    assert response.get('deleted')

    comments_count = get_comment_collection().count_documents({'post_id': post})
    assert comments_count == 0


async def test_user_can_get_post_list(client: AsyncClient, user, token, post):
    response = await client.get(url='api/v1/posts/',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 1
    assert response_data.get('page') == 1
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(post)


async def test_user_can_paginate_post_list(client: AsyncClient, user, token, post, post2):
    response = await client.get(url='api/v1/posts/',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 2
    assert response_data.get('page') == 1
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(post)

    response = await client.get(url='api/v1/posts/?page=2',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 2
    assert response_data.get('page') == 2
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(post2)


async def test_user_can_change_page_size(client: AsyncClient, user, token, post, post2):
    response = await client.get(url='api/v1/posts/?page_size=2',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 2
    assert response_data.get('page') == 1
    assert response_data.get('page_size') == 2

    items = response_data.get('items')
    assert items
    assert len(items) == 2

