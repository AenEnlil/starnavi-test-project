import pytest

from pymongo.errors import DuplicateKeyError

from app.database import get_user_collection
from app.user.service import pwd_context, verify_password, create_user, find_user_by_id
from tests.conftest import USER_DATA


async def test_verify_password_with_correct_password():
    plain_password = 'test123'
    hashed_password = pwd_context.hash(plain_password)
    assert verify_password(plain_password, hashed_password)


async def test_verify_password_with_incorrect_password():
    plain_password = 'test123'
    hashed_password = pwd_context.hash(plain_password)
    assert not verify_password('incorrect_pass', hashed_password)


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


async def test_cannot_create_user_with_existing_email(app, user):
    number_of_existing_users = get_user_collection().count_documents({})
    assert number_of_existing_users

    with pytest.raises(DuplicateKeyError) as _e:
        create_user(USER_DATA)


async def test_find_user_by_id(app, user):
    user_data = find_user_by_id(user)
    assert user_data
    assert user_data.get('email') == USER_DATA.get('email')
