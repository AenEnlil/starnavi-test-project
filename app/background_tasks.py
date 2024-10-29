from app.comments.service import create_comment_in_db
from app.logger import get_logger
from app.vertex_ai_core.core import generate_answer_to_user_comment_as_author_of_post


def answer_to_comment(post_data, comment_data) -> None:
    """
    Automatic answer to user comment
    :param post_data: post data
    :param comment_data: user comment
    :return: None
    """
    try:
        text = generate_answer_to_user_comment_as_author_of_post(post=post_data.get('text'),
                                                                 comment=comment_data.get('text'))
        data = {'text': text, 'post_author_answer': True, 'answered_comment_id': comment_data.get('_id')}
        create_comment_in_db(post_data.get('_id'), post_data.get('user_id'), data)
    except Exception as _e:
        logger = get_logger()
        logger.error(_e, exc_info=True)

