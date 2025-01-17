import pytest

from datetime import datetime

from app.database import get_comment_collection, get_statistic_collection
from app.comments.service import create_comment_in_db, find_comment_by_id, update_comment, delete_comment_in_db, \
    get_post_match_pipeline, update_comments_statistics, get_comment_statistics_for_certain_period, \
    delete_all_comments_related_to_post
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


async def test_update_statistics_create_statistics_if_not_exists(app):
    current_date = datetime.utcnow().date().strftime("%Y-%m-%d")

    existing_statistics = get_statistic_collection().find_one({'date': current_date})
    assert not existing_statistics

    update_comments_statistics(increase_blocked_comments=True)

    existing_statistics = get_statistic_collection().find_one({'date': current_date})
    assert existing_statistics
    assert existing_statistics.get('date') == current_date


async def test_update_statistics_increase_created_comments_count(app):
    current_date = datetime.utcnow().date().strftime("%Y-%m-%d")
    update_comments_statistics(increase_created_comments=True)

    existing_statistics = get_statistic_collection().find_one({'date': current_date})
    assert existing_statistics
    assert existing_statistics.get('blocked_comments') == 0
    assert existing_statistics.get('created_comments') == 1
    assert existing_statistics.get('date') == current_date


async def test_update_statistics_increase_blocked_comments_count(app):
    current_date = datetime.utcnow().date().strftime("%Y-%m-%d")
    update_comments_statistics(increase_blocked_comments=True)

    existing_statistics = get_statistic_collection().find_one({'date': current_date})
    assert existing_statistics
    assert existing_statistics.get('blocked_comments') == 1
    assert existing_statistics.get('created_comments') == 0
    assert existing_statistics.get('date') == current_date


async def test_get_comment_statistics_for_certain_period(comments_statistics):
    existing_statistics = get_statistic_collection().find_one({'_id': comments_statistics})
    assert existing_statistics

    filtered_statistics = get_comment_statistics_for_certain_period('2024-05-12', existing_statistics.get('date'))
    assert filtered_statistics

    items = filtered_statistics.get('items')
    existing_statistics_date = existing_statistics.get('date')
    assert items
    assert existing_statistics_date in items[0]

    statistics_by_day = items[0].get(existing_statistics_date)
    assert statistics_by_day
    assert statistics_by_day.get('created_comments') == existing_statistics.get('created_comments')
    assert statistics_by_day.get('blocked_comments') == existing_statistics.get('blocked_comments')


async def test_delete_all_comments_related_to_post(app, post, post2, comment, comment2, comment_to_another_post):
    document_count = get_comment_collection().count_documents({})
    assert document_count == 3

    delete_all_comments_related_to_post(post)

    document_count = get_comment_collection().count_documents({})
    assert document_count == 1

    assert get_comment_collection().find_one({'_id': comment_to_another_post.id})

