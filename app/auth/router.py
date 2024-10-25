from fastapi import APIRouter, HTTPException
from starlette import status

from app.auth.jwt import AccessToken
from app.auth.service import authenticate_user
from app.auth.schemas import UserLogInSchema
from app import messages

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/login')
async def login_for_access_token(login_data: UserLogInSchema):
    user = authenticate_user(**login_data.model_dump())
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.INCORRECT_LOGIN_INPUT)
    token = AccessToken()
    return {'access_token': token.create_access_token(user.get('email')),
            'token_type': 'bearer'}
