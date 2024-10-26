import pytest

from app.database import get_comment_collection
from app.comments.service import create_comment_in_db, find_comment_by_id, update_comment, delete_comment_in_db, \
    get_post_match_pipeline
from tests.conftest import COMMENT_DATA


async def test_get_post_match_pipeline(app, post):
    pipeline = get_post_match_pipeline(post)

    assert pipeline
    assert type(pipeline) == list
    assert '$match' in pipeline[0]


async def test_user_can_create_comment(app, user, post):
    created_comment_id = create_comment_in_db(data=COMMENT_DATA.copy(), user_id=user, post_id=post)
    assert created_comment_id

    created_comment = get_comment_collection().find_one({'_id': created_comment_id})
    assert created_comment
    assert created_comment.get('text') == COMMENT_DATA.get('text')
    assert created_comment.get('post_id') == post
    assert created_comment.get('author_id') == user


async def test_find_comment_by_id(app, comment):
    number_of_existing_comments = get_comment_collection().count_documents({})
    assert number_of_existing_comments

    found_comment = find_comment_by_id(comment.id)
    assert found_comment
    assert found_comment.get('_id') == comment.id


async def test_update_comment(app, comment):
    old_comment = find_comment_by_id(comment.id)
    new_data = {'title': 'changed'}

    assert new_data.get('title') != old_comment.get('title')

    updated_comment_id = update_comment(comment.id, new_data)
    assert updated_comment_id

    updated_comment = find_comment_by_id(updated_comment_id)
    assert updated_comment.get('title') == new_data.get('title')
    assert updated_comment.get('_id') == old_comment.get('_id')


async def test_delete_comment(app, comment):
    existing_comments_count = get_comment_collection().count_documents({})
    assert existing_comments_count

    result = delete_comment_in_db(comment.id)
    assert result

    existing_comments_count = get_comment_collection().count_documents({})
    assert not existing_comments_count

