import pytest
import json

from httpx import AsyncClient
from starlette import status

from app import messages
from app.custom_fields import PyObjectId
from tests.conftest import COMMENT_DATA


async def test_not_authenticated_user_cant_create_comment(client: AsyncClient, post):
    response = await client.post(url=f'api/v1/posts/{post}/comments/', data=json.dumps(COMMENT_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_update_comment(client: AsyncClient, post, comment):
    response = await client.patch(url=f'api/v1/posts/{post}/comments/{comment.id}', data=json.dumps(COMMENT_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_delete_comment(client: AsyncClient, post, comment):
    response = await client.delete(url=f'api/v1/posts/{post}/comments/{comment.id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_cant_create_comment_for_non_existing_post(client: AsyncClient, user, token):
    post_id = PyObjectId()

    response = await client.post(url=f'api/v1/posts/{post_id}/comments/',
                                 data=json.dumps(COMMENT_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = response.json()
    assert response
    assert response.get('detail') == messages.POST_NOT_FOUND


async def test_user_cant_edit_non_existing_comment(client: AsyncClient, user, token, post):
    comment_id = PyObjectId()

    response = await client.patch(url=f'api/v1/posts/{post}/comments/{comment_id}',
                                  data=json.dumps(COMMENT_DATA.copy()),
                                  headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = response.json()
    assert response
    assert response.get('detail') == messages.COMMENT_NOT_FOUND


async def test_user_cant_delete_non_existing_comment(client: AsyncClient, user, token, post):
    comment_id = PyObjectId()

    response = await client.delete(url=f'api/v1/posts/{post}/comments/{comment_id}',
                                   headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = response.json()
    assert response
    assert response.get('detail') == messages.COMMENT_NOT_FOUND


async def test_user_cant_edit_someone_else_comment(client: AsyncClient, user, token, user2, token2, post, comment):
    new_data = {'text': 'new text'}
    assert new_data.get('text') != comment.text

    response = await client.patch(url=f'api/v1/posts/{post}/comments/{comment.id}',
                                  data=json.dumps(new_data.copy()),
                                  headers={'Authorization': f'Bearer {token2}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()
    assert response
    assert response.get('detail') == messages.COMMENT_UPDATE_NOT_ALLOWED


async def test_user_cant_delete_someone_else_comment(client: AsyncClient, user, token, user2, token2, post, comment):
    response = await client.delete(url=f'api/v1/posts/{post}/comments/{comment.id}',
                                   headers={'Authorization': f'Bearer {token2}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = response.json()
    assert response
    assert response.get('detail') == messages.COMMENT_DELETE_NOT_ALLOWED


async def test_user_can_create_comment(client: AsyncClient, user, token, post):
    response = await client.post(url=f'api/v1/posts/{post}/comments/',
                                 data=json.dumps(COMMENT_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('text') == COMMENT_DATA.get('text')
    assert response_data.get('author_id') == str(user)
    assert response_data.get('post_id') == str(post)


async def test_user_can_edit_comment(client: AsyncClient, user, token, post, comment):
    new_data = {'text': 'new text'}
    assert new_data.get('text') != comment.text

    response = await client.patch(url=f'api/v1/posts/{post}/comments/{comment.id}',
                                  data=json.dumps(new_data.copy()),
                                  headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('text') == new_data.get('text')
    assert response_data.get('_id') == str(comment.id)
    assert response_data.get('author_id') == str(comment.author_id)
    assert response_data.get('post_id') == str(comment.post_id)


async def test_user_can_delete_comment(client: AsyncClient, user, token, post, comment):
    response = await client.delete(url=f'api/v1/posts/{post}/comments/{comment.id}',
                                   headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('deleted')
