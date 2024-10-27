from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException
from starlette import status


from google.api_core.exceptions import ResourceExhausted
from pydantic import BaseModel, Field, model_validator

from app.config import get_settings
from app.messages import AI_REQUEST_QUOTA_EXCEEDED, AI_VALIDATION_ERROR
from app.vertex_ai_core.core import get_result_of_ai_validation
from app.custom_fields import PyObjectId


class PostBaseSchema(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=2000)


class PostCreateInSchema(PostBaseSchema):

    @model_validator(mode='after')
    def validate_attrs(self):
        if get_settings().USE_AI_FOR_TEXT_VALIDATION:
            try:
                validation_result = get_result_of_ai_validation({"title": self.title, "text": self.text})
                if not validation_result.get('result'):
                    failed_fields = validation_result.get('failed_fields')
                    raise ValueError(f'following fields contains offensive language: {failed_fields}')
            except ValueError as _e:
                raise ValueError(_e.args[0])
            except ResourceExhausted:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AI_REQUEST_QUOTA_EXCEEDED)
            except Exception as _e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AI_VALIDATION_ERROR)
        return self


class PostCreateSchema(PostBaseSchema):
    user_id: PyObjectId


class PostUpdateSchema(PostBaseSchema):
    title: Optional[str] = Field(default=None, example='Post', min_length=1, max_length=100)
    text: Optional[str] = Field(default=None, example='some text', min_length=1, max_length=2000)


class PostReadSchema(PostBaseSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    user_id: PyObjectId
    updated_at: datetime
    created_at: datetime


class PostReadPaginationSchema(BaseModel):
    total_items_count: int
    page_size: int
    page: int
    items: List[PostReadSchema] = []



