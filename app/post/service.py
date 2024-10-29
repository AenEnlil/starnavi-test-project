from datetime import datetime

from app.database import get_post_collection
from app.custom_fields import PyObjectId
from app.post.schema import PostCreateSchema
from app.comments.service import delete_all_comments_related_to_post


def create_post_in_db(post_data: dict, user_id: PyObjectId) -> PyObjectId:
    """
    Creates post in database
    :param post_data: post data
    :param user_id: id of user that creates post
    :return: id of created post
    """
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = PostCreateSchema(**post_data, user_id=user_id).model_dump()
    data.update({'updated_at': current_time, 'created_at': current_time})

    result = get_post_collection().insert_one(data)
    return result.inserted_id


def find_post_by_id(post_id: PyObjectId) -> dict:
    """
    Looks up the post in the database
    :param post_id: id of post that need to be found
    :return: post data from database
    """
    return get_post_collection().find_one({'_id': post_id})


def check_post_duplication_from_user(title: str, user_id: PyObjectId) -> bool:
    """
    Checks if user already create post with given title
    :param title: Post title
    :param user_id: User id
    :return: bool result of this check
    """
    result = get_post_collection().find_one({'title': title, 'user_id': user_id})
    return bool(result)


def update_post(post_id: PyObjectId, data: dict) -> PyObjectId:
    """
    Updates post in the database using passed data
    :param post_id: id of post that need to be updated
    :param data: data that will be used to update
    :return: post id
    """
    data.update({'updated_at': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    get_post_collection().update_one({'_id': post_id}, {'$set': data})
    return post_id


def delete_post_in_db(post_id: PyObjectId) -> bool:
    """
    Removes post from database
    :param post_id: id of post that need to be deleted
    :return: deletion result
    """
    result = get_post_collection().delete_one({'_id': post_id})
    delete_all_comments_related_to_post(post_id)
    return bool(result.deleted_count)
