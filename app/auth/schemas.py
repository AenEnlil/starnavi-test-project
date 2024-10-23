from pydantic import BaseModel, EmailStr, Field

from app.custom_fields import PyObjectId


class UserLogInSchema(BaseModel):
    email: EmailStr
    password: str


class UserReadSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    email: EmailStr
    password: str


class TokenData(BaseModel):
    email: EmailStr

