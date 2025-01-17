import pytest

from app.database import get_post_collection
from app.post.service import find_post_by_id, create_post_in_db, update_post, delete_post_in_db, \
    check_post_duplication_from_user
from tests.conftest import POST_DATA


async def test_user_can_create_post_in_db(app, user):
    number_of_existing_posts = get_post_collection().count_documents({})
    assert not number_of_existing_posts

    created_post_id = create_post_in_db(POST_DATA.copy(), user_id=user)
    assert created_post_id

    created_post = get_post_collection().find_one({'_id': created_post_id})
    assert created_post
    assert created_post.get('text') == POST_DATA.get('text')
    assert created_post.get('user_id') == user


async def test_find_post_by_id(app, post):
    number_of_existing_posts = get_post_collection().count_documents({})
    assert number_of_existing_posts

    found_post = find_post_by_id(post)
    assert found_post
    assert found_post.get('_id') == post


async def test_update_post(app, post):
    old_post = find_post_by_id(post)
    new_data = {'title': 'changed'}

    assert new_data.get('title') != old_post.get('title')

    updated_post_id = update_post(post, new_data)
    assert updated_post_id

    updated_post = find_post_by_id(updated_post_id)
    assert updated_post.get('title') == new_data.get('title')
    assert updated_post.get('_id') == old_post.get('_id')


async def test_delete_post(app, post):
    existing_posts_count = get_post_collection().count_documents({})
    assert existing_posts_count

    result = delete_post_in_db(post)
    assert result

    existing_posts_count = get_post_collection().count_documents({})
    assert not existing_posts_count


async def test_check_post_duplication_from_user(app, post):
    post_data = find_post_by_id(post)
    assert post_data

    assert check_post_duplication_from_user(post_data.get('title'), post_data.get('user_id'))
    assert not check_post_duplication_from_user('new_title', post_data.get('user_id'))

