from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import get_settings

settings = get_settings()

mongo_client = MongoClient(settings.MONGO_URL)
db = mongo_client[settings.DATABASE_NAME]


USER_DOC = 'users'
POST_DOC = 'posts'
COMMENT_DOC = 'comments'
STATISTICS_DOC = 'statistics'

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


def get_collection_by_name(name: str) -> Collection:
    """
    get collection by name
    :param name: name of collection
    :return:  collection
    """
    return db.get_collection(name)


def get_statistic_collection() -> Collection:
    """
    returns statistics collection
    :return: statistics collection
    """
    return db.get_collection(STATISTICS_DOC)
