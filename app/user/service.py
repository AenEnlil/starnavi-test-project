from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.custom_fields import PyObjectId
from app.user.schemas import UserCreateSchema
from app.auth.service import pwd_context
from app.database import get_user_collection


def find_user_by_id(user_id: ObjectId) -> dict:
    """
    Looks up the user in the database
    :param user_id: id of user that need to be found
    :return: user data from database
    """
    return get_user_collection().find_one({'_id': user_id})


def create_user(user_data: dict) -> PyObjectId:
    """
    Creates user with hashed password in database
    :param user_data: data that will be used to create user
    :return: id of created user
    """
    data = UserCreateSchema(**user_data).model_dump()
    user_dict = jsonable_encoder(data)
    user_dict['password'] = pwd_context.hash(user_dict['password'])
    result = get_user_collection().insert_one(user_dict)
    return result.inserted_id


def update_user(user_id: PyObjectId, data: dict) -> PyObjectId:
    """
    Updates user in the database using passed data
    :param user_id: id of user that need to be updated
    :param data: data that will be used to update
    :return: user id
    """
    get_user_collection().update_one({'_id': user_id}, {'$set': data})
    return user_id
