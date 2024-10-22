from fastapi import APIRouter, HTTPException
from starlette import status
from pymongo.errors import DuplicateKeyError

from app.user import messages
from app.user.schemas import UserRegisterSchema, UserResponseSchema
from app.user.service import create_user, find_user_by_id

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def register_user(user_data: UserRegisterSchema):
    try:
        created_user_id = create_user(user_data.model_dump())
        created_user = find_user_by_id(created_user_id)
        return created_user
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.USER_ALREADY_EXISTS)
