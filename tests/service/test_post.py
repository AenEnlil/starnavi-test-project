import pytest

from app.database import get_post_collection
from app.post.service import find_post_by_id, create_post_in_db
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
