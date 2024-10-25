from datetime import datetime

from app.custom_fields import PyObjectId
from app.database import get_comment_collection
from app.comments.schemas import CommentCreateSchema


def create_comment_in_db(post_id: PyObjectId, user_id: PyObjectId, data: dict):
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = CommentCreateSchema(**data, post_id=post_id, author_id=user_id).model_dump()
    data.update({'updated_at': current_time, 'created_at': current_time})
    result = get_comment_collection().insert_one(data)
    return result.inserted_id


def find_comment_by_id(comment_id: PyObjectId):
    return get_comment_collection().find_one({'_id': comment_id})


def update_comment(comment_id: PyObjectId, data: dict):
    data.update({'updated_at': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    get_comment_collection().update_one({'_id': comment_id}, {'$set': data})
    return comment_id


def delete_comment_in_db(comment_id: PyObjectId):
    result = get_comment_collection().delete_one({'_id': comment_id})
    return bool(result.deleted_count)
