import pytest
import json

from datetime import datetime
from httpx import AsyncClient
from starlette import status

from app import messages
from app.database import get_statistic_collection
from app.custom_fields import PyObjectId
from tests.conftest import COMMENT_DATA


async def test_not_authenticated_user_cant_create_comment(client: AsyncClient, post):
    response = await client.post(url=f'api/v1/posts/{post}/comments/', data=json.dumps(COMMENT_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_get_comment_list(client: AsyncClient, post):
    response = await client.get(url=f'api/v1/posts/{post}/comments/')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_update_comment(client: AsyncClient, post, comment):
    response = await client.patch(url=f'api/v1/posts/{post}/comments/{comment.id}', data=json.dumps(COMMENT_DATA.copy()))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_delete_comment(client: AsyncClient, post, comment):
    response = await client.delete(url=f'api/v1/posts/{post}/comments/{comment.id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_not_authenticated_user_cant_get_comment_statistics(client: AsyncClient):
    response = await client.get(url=f'api/v1/statistics/comments-daily-breakdown')

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
    current_date = datetime.utcnow().date().strftime("%Y-%m-%d")
    existing_statistics = get_statistic_collection().find_one({'date': current_date})
    assert not existing_statistics

    response = await client.post(url=f'api/v1/posts/{post}/comments/',
                                 data=json.dumps(COMMENT_DATA.copy()),
                                 headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()

    assert response_data
    assert response_data.get('text') == COMMENT_DATA.get('text')
    assert response_data.get('author_id') == str(user)
    assert response_data.get('post_id') == str(post)

    existing_statistics = get_statistic_collection().find_one({'date': current_date})
    assert existing_statistics
    assert existing_statistics.get('created_comments') == 1
    assert existing_statistics.get('blocked_comments') == 0


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


async def test_user_can_get_comment_list(client: AsyncClient, user, token, post, comment):
    response = await client.get(url=f'api/v1/posts/{post}/comments/',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 1
    assert response_data.get('page') == 1
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(comment.id)


async def test_user_not_get_comments_from_another_post(client: AsyncClient, user, token, post, comment,
                                                       comment_to_another_post):
    response = await client.get(url=f'api/v1/posts/{post}/comments/',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 1
    assert response_data.get('page') == 1
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(comment.id)
    assert items[0].get('_id') != str(comment_to_another_post.id)
    assert items[0].get('post_id') == str(post)
    assert items[0].get('post_id') != str(comment_to_another_post.post_id)


async def test_user_can_paginate_comment_list(client: AsyncClient, user, token, post, comment, comment2):
    response = await client.get(url=f'api/v1/posts/{post}/comments/',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 2
    assert response_data.get('page') == 1
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(comment.id)

    response = await client.get(url=f'api/v1/posts/{post}/comments/?page=2',
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data
    assert response_data.get('total_items_count') == 2
    assert response_data.get('page') == 2
    assert response_data.get('page_size') == 1

    items = response_data.get('items')
    assert items
    assert items[0].get('_id') == str(comment2.id)


async def test_user_can_change_comment_list_page_size(client: AsyncClient, user, token, post, comment, comment2):
    response = await client.get(url=f'api/v1/posts/{post}/comments/?page_size=2',
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


async def test_user_can_get_comment_statistics(client: AsyncClient, user, token, comments_statistics):
    existing_statistics = get_statistic_collection().find_one({'_id': comments_statistics})
    assert existing_statistics
    stat_date = existing_statistics.get('date')

    response = await client.get(url=f"api/v1/statistics/comments-daily-breakdown?date_from=2024-04-12&date_to={stat_date}",
                                headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data

    items = response_data.get('items')
    assert items
    assert stat_date in items[0]

    daily_statistics = items[0].get(stat_date)
    assert daily_statistics
    assert daily_statistics.get('created_comments') == existing_statistics.get('created_comments')
    assert daily_statistics.get('blocked_comments') == existing_statistics.get('blocked_comments')
