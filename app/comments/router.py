from typing import Annotated

from datetime import datetime, timedelta

from apscheduler.triggers.date import DateTrigger
from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from starlette.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserReadSchema
from app.background_tasks import answer_to_comment
from app.comments.schemas import CommentCreateInSchema, CommentUpdateSchema, CommentReadSchema, \
    CommentReadPaginationSchema, CommentStatisticsResponseSchema
from app.custom_fields import PyObjectId
from app import messages
from app.database import COMMENT_DOC
from app.service import paginate_collection
from app.post.service import find_post_by_id
from app.comments.service import create_comment_in_db, find_comment_by_id, delete_comment_in_db, update_comment, \
    get_post_match_pipeline, update_comments_statistics, get_comment_statistics_for_certain_period
from app.user.service import find_user_by_id

router = APIRouter(
    prefix='/posts/{post_id}/comments',
    tags=['comments']
)

statistics_router = APIRouter(
    prefix='/statistics',
    tags=['statistics']
)


@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=CommentReadSchema)
async def create_comment(post_id: PyObjectId, comment: CommentCreateInSchema,
                         current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)

    created_comment_id = create_comment_in_db(post_id, current_user.id, comment.model_dump())
    update_comments_statistics(increase_created_comments=True)
    created_comment = find_comment_by_id(created_comment_id)

    post_author_data = find_user_by_id(post.get('user_id'))
    if post_author_data.get('automatic_response_enabled') and post_author_data.get('_id') != current_user.id:
        from app.main import scheduler
        executing_date = datetime.now() + timedelta(minutes=post_author_data.get('automatic_response_delay_in_minutes'))
        scheduler.add_job(answer_to_comment, DateTrigger(run_date=executing_date), [post, created_comment],
                          misfire_grace_time=3600)
    return created_comment


@router.get(path='/', status_code=status.HTTP_200_OK, response_model=CommentReadPaginationSchema)
async def get_comments(post_id: PyObjectId,
                       current_user: Annotated[UserReadSchema, Depends(get_current_user)],
                       page: int = Query(1, gt=0, lt=2147483647),
                       page_size: int = Query(1, gt=0, lt=2147483647)):
    return paginate_collection(collection_name=COMMENT_DOC, pipeline=get_post_match_pipeline(post_id),
                               page=page, items_per_page=page_size)


@router.patch(path='/{comment_id}', status_code=status.HTTP_200_OK, response_model=CommentReadSchema)
async def edit_comment(post_id: PyObjectId, comment_id: PyObjectId, comment_data: CommentUpdateSchema,
                       current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    comment = find_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)
    if comment.get('author_id') != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.COMMENT_UPDATE_NOT_ALLOWED)

    updated_comment_id = update_comment(comment_id, comment_data.model_dump(exclude_unset=True, exclude_none=True))
    updated_comment = find_comment_by_id(updated_comment_id)
    return updated_comment


@router.delete(path='/{comment_id}')
async def delete_comment(post_id: PyObjectId, comment_id: PyObjectId,
                         current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    comment = find_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)
    if comment.get('author_id') != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.COMMENT_DELETE_NOT_ALLOWED)

    result = delete_comment_in_db(comment_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={'deleted': result})


@statistics_router.get(path='/comments-daily-breakdown', status_code=status.HTTP_200_OK,
                       response_model=CommentStatisticsResponseSchema)
async def read_comments_daily_breakdown(current_user: Annotated[UserReadSchema, Depends(get_current_user)],
                                        date_from: datetime = Query(description='The date from which the search for '
                                                                                'comment statistics will be performed',
                                                                    example='2024-12-23'),
                                        date_to: datetime = Query(description='The date until which the search for '
                                                                              'comment statistics will be performed',
                                                                  example='2024-12-23')):
    comments_statistics = get_comment_statistics_for_certain_period(date_from=date_from.date().strftime("%Y-%m-%d"),
                                                                    date_to=date_to.date().strftime("%Y-%m-%d"))
    return comments_statistics
