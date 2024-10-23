from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.auth.service import pwd_context
from app.database import get_user_collection


def find_user_by_id(user_id: ObjectId):
    return get_user_collection().find_one({'_id': user_id})


def create_user(user_data: dict):
    user_dict = jsonable_encoder(user_data)
    user_dict['password'] = pwd_context.hash(user_dict['password'])
    result = get_user_collection().insert_one(user_dict)
    return result.inserted_id

