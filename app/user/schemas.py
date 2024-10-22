from pydantic import BaseModel, EmailStr, field_validator, Field

from app.custom_fields import PyObjectId


class UserBaseSchema(BaseModel):
    email: EmailStr


class UserRegisterSchema(UserBaseSchema):
    password: str

    @field_validator('password')
    @classmethod
    def password_validator(cls, value) -> str:
        value = value.strip()
        if not value:
            raise ValueError('Empty field')
        return value


class UserResponseSchema(UserBaseSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
