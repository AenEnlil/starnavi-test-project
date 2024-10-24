from app.database import get_post_collection
from app.custom_fields import PyObjectId
from app.post.schema import PostCreateSchema


def create_post_in_db(post_data: dict, user_id: PyObjectId):
    data = PostCreateSchema(**post_data, user_id=user_id).model_dump()
    result = get_post_collection().insert_one(data)
    return result.inserted_id


def find_post_by_id(post_id: PyObjectId):
    return get_post_collection().find_one({'_id': post_id})


def update_post(post_id: PyObjectId, data: dict):
    get_post_collection().update_one({'_id': post_id}, {'$set': data})
    return post_id

