from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from pymongo.errors import DuplicateKeyError

from app import messages
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserReadSchema
from app.custom_fields import PyObjectId
from app.user.schemas import UserRegisterSchema, UserResponseSchema, UserSettingReadSchema, UserSettingsUpdateSchema
from app.user.service import create_user, find_user_by_id, update_user

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


@router.get(path='/{user_id}/settings', status_code=status.HTTP_200_OK, response_model=UserSettingReadSchema)
async def get_user_settings(user_id: PyObjectId, current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.USER_SETTINGS_READ_NOT_ALLOWED)

    user_data = find_user_by_id(user_id)
    return user_data


@router.patch(path='/{user_id}/settings', status_code=status.HTTP_200_OK, response_model=UserSettingReadSchema)
async def update_user_settings(user_id: PyObjectId, settings: UserSettingsUpdateSchema,
                               current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.USER_SETTINGS_UPDATE_NOT_ALLOWED)

    updated_user_id = update_user(user_id, settings.model_dump(exclude_unset=True, exclude_none=True))
    updated_user = find_user_by_id(updated_user_id)
    return updated_user
