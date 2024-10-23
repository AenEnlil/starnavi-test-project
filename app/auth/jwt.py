
import jwt

from datetime import datetime, timedelta

from .exceptions import TokenError
from app.config import get_settings


class AccessToken:
    """
    Class for creating and decoding JWT token
    """

    def __init__(self, current_time: datetime | None = None):
        self._current_time = current_time if current_time else datetime.utcnow()
        self._settings = get_settings()

    def create_access_token(self, email: str) -> str:
        expire = self._current_time + timedelta(minutes=self._settings.ACCESS_TOKEN_LIFETIME_MINUTES)
        payload = {'exp': expire, 'sub': email}
        encoded_jwt = jwt.encode(payload, self._settings.SECRET_KEY, algorithm=self._settings.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._settings.SECRET_KEY, algorithms=[self._settings.ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise TokenError('token is incorrect')
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenError('token expired')
