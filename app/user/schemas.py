from typing import Optional

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


class UserCreateSchema(UserBaseSchema):
    password: str
    automatic_response_enabled: bool = False
    automatic_response_delay_in_minutes: int = 15


class UserResponseSchema(UserBaseSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')


class UserSettingsUpdateSchema(BaseModel):
    automatic_response_enabled: Optional[bool] = Field(default=None)
    automatic_response_delay_in_minutes: Optional[int] = Field(default=None, gt=0, le=600)


class UserSettingReadSchema(BaseModel):
    automatic_response_enabled: bool
    automatic_response_delay_in_minutes: int
