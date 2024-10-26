from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated
from starlette import status
from starlette.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserReadSchema
from app.custom_fields import PyObjectId
from app import messages
from app.database import POST_DOC
from app.service import paginate_collection
from app.post.service import create_post_in_db, find_post_by_id, update_post, delete_post_in_db, \
    check_post_duplication_from_user
from app.post.schema import PostCreateInSchema, PostReadSchema, PostUpdateSchema, PostReadPaginationSchema

router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=PostReadSchema)
async def create_post(post: PostCreateInSchema, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if check_post_duplication_from_user(post.title, current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_ALREADY_EXISTS)

    created_post_id = create_post_in_db(post.model_dump(), user_id=current_user.id)
    created_post = find_post_by_id(created_post_id)
    return created_post


@router.get(path='/', status_code=status.HTTP_200_OK, response_model=PostReadPaginationSchema)
async def get_list_of_posts(current_user: Annotated[UserReadSchema, Depends(get_current_user)],
                            page: int = Query(1, gt=0, lt=2147483647),
                            page_size: int = Query(1, gt=0, lt=2147483647)):
    return paginate_collection(collection_name=POST_DOC, pipeline=[], page=page, items_per_page=page_size)


@router.get(path='/{post_id}', status_code=status.HTTP_200_OK, response_model=PostReadSchema)
async def read_post(post_id: PyObjectId, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_NOT_FOUND)

    return post


@router.patch(path='/{post_id}', status_code=status.HTTP_200_OK, response_model=PostReadSchema)
async def edit_post(post_id: PyObjectId, post_data: PostUpdateSchema, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    old_post = find_post_by_id(post_id)
    if not old_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)
    if old_post.get('user_id') != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_EDIT_NOT_ALLOWED)

    updated_post_id = update_post(post_id, post_data.model_dump(exclude_unset=True, exclude_none=True))
    updated_post = find_post_by_id(updated_post_id)
    return updated_post


@router.delete(path='/{post_id}')
async def delete_post(post_id: PyObjectId, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)
    if post.get('user_id') != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_DELETE_NOT_ALLOWED)

    result = delete_post_in_db(post_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={'deleted': result})
