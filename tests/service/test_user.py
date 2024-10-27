import pytest

from app.database import get_user_collection
from app.user.service import create_user, find_user_by_id, update_user
from tests.conftest import USER_DATA


async def test_create_user(app):
    number_of_existing_users = get_user_collection().count_documents({})
    assert not number_of_existing_users

    created_user_id = create_user(USER_DATA)
    number_of_existing_users = get_user_collection().count_documents({})

    assert created_user_id
    assert number_of_existing_users

    created_user_data = get_user_collection().find_one({'_id': created_user_id})
    assert created_user_data
    assert created_user_data.get('email') == USER_DATA.get('email')


async def test_find_user_by_id(app, user):
    user_data = find_user_by_id(user)
    assert user_data
    assert user_data.get('email') == USER_DATA.get('email')


async def test_update_user(app, user):
    user_data = find_user_by_id(user)
    new_data = {'automatic_response_enabled': True}
    assert user_data.get('automatic_response_enabled') != new_data.get('automatic_response_enabled')

    updated_user_id = update_user(user, new_data)
    assert updated_user_id == user

    updated_user_data = find_user_by_id(updated_user_id)

    assert updated_user_data
    assert updated_user_data.get('automatic_response_enabled') == new_data.get('automatic_response_enabled')
    assert updated_user_data.get('email') == user_data.get('email')

