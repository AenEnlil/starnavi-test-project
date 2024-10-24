import pytest

from typing import Generator, Any

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.auth.jwt import AccessToken
from app.main import get_application
from app.config import get_settings
from app.database import mongo_client
from app.comments.schemas import CommentReadSchema
from app.comments.service import create_comment_in_db, find_comment_by_id
from app.post.service import create_post_in_db
from app.user.service import create_user

settings = get_settings()

USER_DATA = {
    'email': 'test_user@email.com',
    'password': 'pass123'
}

USER2_DATA = {
    'email': 'test_user2@email.com',
    'password': '654F3'
}

POST_DATA = {
    'title': 'Test Post',
    'text': 'some text'
}

COMMENT_DATA = {
    'text': 'test comment'
}


@pytest.fixture
async def app() -> Generator[FastAPI, Any, None]:
    _app = get_application()
    yield _app

    mongo_client.drop_database(get_settings().DATABASE_NAME)


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://') as test_client:
        yield test_client


@pytest.fixture
async def user():
    created_user_id = create_user(USER_DATA)
    return created_user_id


@pytest.fixture
async def user2():
    created_user_id = create_user(USER2_DATA)
    return created_user_id


@pytest.fixture
async def token():
    return AccessToken().create_access_token(USER_DATA.get('email'))


@pytest.fixture
async def token2():
    return AccessToken().create_access_token(USER2_DATA.get('email'))


@pytest.fixture
async def post(user):
    created_post_id = create_post_in_db(POST_DATA.copy(), user_id=user)
    return created_post_id


@pytest.fixture
async def comment(user, post) -> CommentReadSchema:
    comment_data = COMMENT_DATA.copy()
    created_comment_id = create_comment_in_db(post, user, comment_data)
    return CommentReadSchema(**find_comment_by_id(created_comment_id))
