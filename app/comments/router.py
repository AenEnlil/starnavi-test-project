from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from starlette.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserReadSchema
from app.comments.schemas import CommentCreateInSchema, CommentUpdateSchema, CommentReadSchema, \
    CommentReadPaginationSchema
from app.custom_fields import PyObjectId
from app import messages
from app.database import COMMENT_DOC
from app.service import paginate_collection
from app.post.service import find_post_by_id
from app.comments.service import create_comment_in_db, find_comment_by_id, delete_comment_in_db, update_comment, \
    get_post_match_pipeline

router = APIRouter(
    prefix='/posts/{post_id}/comments',
    tags=['comments']
)


@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=CommentReadSchema)
async def create_comment(post_id: PyObjectId, comment: CommentCreateInSchema,
                         current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)

    created_comment_id = create_comment_in_db(post_id, current_user.id, comment.model_dump())
    created_comment = find_comment_by_id(created_comment_id)
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

