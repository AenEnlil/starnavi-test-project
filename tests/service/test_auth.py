import pytest

from app.auth.service import pwd_context, verify_password, find_user_by_email, authenticate_user
from tests.conftest import USER_DATA


async def test_find_user_by_email(app, user):
    email = USER_DATA.get('email')
    user_found = find_user_by_email(email)

    assert user_found
    assert user_found.get('email') == email


async def test_verify_password_with_correct_password():
    plain_password = 'test123'
    hashed_password = pwd_context.hash(plain_password)
    assert verify_password(plain_password, hashed_password)


async def test_verify_password_with_incorrect_password():
    plain_password = 'test123'
    hashed_password = pwd_context.hash(plain_password)
    assert not verify_password('incorrect_pass', hashed_password)


async def test_authenticate_not_existing_user():
    result = authenticate_user('email123@m.com', 'pass')

    assert not result


async def test_authenticate_user_with_incorrect_password(app, user):
    found_user = find_user_by_email(USER_DATA.get('email'))
    assert found_user

    result = authenticate_user(found_user.get('email'), 'pass')
    assert not result


async def test_authenticate_user_with_correct_data(app, user):
    result = authenticate_user(USER_DATA.get('email'), USER_DATA.get('password'))
    assert result
