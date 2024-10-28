from typing import Mapping

from passlib.context import CryptContext

from app.database import get_user_collection

pwd_context = CryptContext(schemes=['bcrypt'])


def find_user_by_email(email: str) -> dict:
    """
    Looks up the user in the database by email
    :param email: user email
    :return: user data from database
    """
    return get_user_collection().find_one({'email': email})


def authenticate_user(email: str, password: str) -> Mapping | bool:
    """
    Authenticates user using passed email and password
    :param email: user email that will be used for authentication
    :param password: user password that will be used for authentication
    :return: If user authenticated returns user data, otherwise returns False
    """
    user = find_user_by_email(email)
    if not user:
        return False

    if not verify_password(password, user.get('password')):
        return False

    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if plain password and hashed password are the same
    :param plain_password: plain password from user
    :param hashed_password: hashed password from database
    :return: True if passwords match, else False
    """
    return pwd_context.verify(plain_password, hashed_password)
