from bson import ObjectId
from passlib.context import CryptContext

from app.database import get_user_collection

pwd_context = CryptContext(schemes=['bcrypt'])


def find_user_by_id(user_id: ObjectId):
    return get_user_collection().find_one({'_id': user_id})


def create_user(user: dict):
    user['password'] = pwd_context.hash(user['password'])
    result = get_user_collection().insert_one(user)
    return result.inserted_id


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
