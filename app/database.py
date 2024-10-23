from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import get_settings

settings = get_settings()

mongo_client = MongoClient(settings.MONGO_URL)
db = mongo_client[settings.DATABASE_NAME]


USER_DOC = 'users'
POST_DOC = 'posts'
COMMENT_DOC = 'comments'

db.users.create_index(['email'], unique=True)


def get_user_collection() -> Collection:
    """
    returns user collection
    :return: user collection
    """
    return db.get_collection(USER_DOC)


def get_post_collection() -> Collection:
    """
    returns post collection
    :return: post collection
    """
    return db.get_collection(POST_DOC)


def get_comment_collection() -> Collection:
    """
    returns comment collection
    :return: comment collection
    """
    return db.get_collection(COMMENT_DOC)

