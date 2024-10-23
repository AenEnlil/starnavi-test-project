from passlib.context import CryptContext

from app.database import get_user_collection

pwd_context = CryptContext(schemes=['bcrypt'])


def find_user_by_email(email: str):
    return get_user_collection().find_one({'email': email})


def authenticate_user(email: str, password: str):
    user = find_user_by_email(email)
    if not user:
        return False

    if not verify_password(password, user.get('password')):
        return False

    return user


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
