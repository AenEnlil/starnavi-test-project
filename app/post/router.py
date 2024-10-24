from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from starlette import status

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserReadSchema
from app.custom_fields import PyObjectId
from app.post import messages
from app.post.service import create_post_in_db, find_post_by_id
from app.post.schema import PostCreateInSchema, PostReadSchema


router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PostReadSchema)
async def create_post(post: PostCreateInSchema, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    created_post_id = create_post_in_db(post.model_dump(), user_id=current_user.id)
    created_post = find_post_by_id(created_post_id)
    return created_post


@router.get('/', status_code=status.HTTP_200_OK)
async def get_list_of_posts(current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    pass


@router.get('/{post_id}', status_code=status.HTTP_200_OK, response_model=PostReadSchema)
async def read_post(post_id: PyObjectId, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_NOT_FOUND)

    return post


@router.patch('/{post_id}', status_code=status.HTTP_200_OK)
async def update_post(post_id: int):
    pass


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    pass
