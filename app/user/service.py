from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.custom_fields import PyObjectId
from app.user.schemas import UserCreateSchema
from app.auth.service import pwd_context
from app.database import get_user_collection


def find_user_by_id(user_id: ObjectId):
    return get_user_collection().find_one({'_id': user_id})


def create_user(user_data: dict):
    data = UserCreateSchema(**user_data).model_dump()
    user_dict = jsonable_encoder(data)
    user_dict['password'] = pwd_context.hash(user_dict['password'])
    result = get_user_collection().insert_one(user_dict)
    return result.inserted_id


def update_user(user_id: PyObjectId, data: dict):
    get_user_collection().update_one({'_id': user_id}, {'$set': data})
    return user_id
