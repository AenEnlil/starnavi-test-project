
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from app.auth.exceptions import UserNotFound
from app.auth.jwt import AccessToken
from app.auth.service import find_user_by_email
from app.auth.schemas import UserReadSchema, TokenData
from app import messages


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail=messages.TOKEN_DECODE_ERROR)
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(token: str) -> bool:
        """
        Checks that token is valid and unexpired
        :param token: jwt token that will be checked
        :return: returns result of the check
        """
        is_token_valid: bool = True

        try:
            payload = AccessToken().decode_token(token)
            email = payload.get('sub')

            if email is None:
                is_token_valid = False

        except Exception as e:
            is_token_valid = False

        return is_token_valid


async def get_current_user(token: str = Depends(JWTBearer())):
    try:
        payload = AccessToken().decode_token(token)
        token_data = TokenData(email=payload.get('sub'))
        user = find_user_by_email(token_data.email)
        if not user:
            raise UserNotFound
        return UserReadSchema(**user)

    except ValueError as e:
        raise HTTPException(status_code=403, detail=messages.EMAIL_VALIDATION_ERROR)

    except Exception as e:
        raise HTTPException(status_code=403, detail=messages.CREDENTIALS_INCORRECT)
