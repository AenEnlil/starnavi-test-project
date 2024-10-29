from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException
from google.api_core.exceptions import ResourceExhausted
from pydantic import BaseModel, Field, model_validator, field_serializer
from starlette import status

from app.config import get_settings
from app.custom_fields import PyObjectId
from app.logger import get_logger
from app.vertex_ai_core.core import get_result_of_ai_validation
from app.messages import AI_VALIDATION_ERROR, AI_REQUEST_QUOTA_EXCEEDED


class CommentBaseSchema(BaseModel):
    text: str = Field(min_length=3, max_length=1000)


class CommentCreateInSchema(CommentBaseSchema):

    @model_validator(mode='after')
    def validate_attrs(self):
        if get_settings().USE_AI_FOR_TEXT_VALIDATION:
            try:
                validation_result = get_result_of_ai_validation({"text": self.text})
                if not validation_result.get('result'):
                    failed_fields = validation_result.get('failed_fields')

                    from app.comments.service import update_comments_statistics
                    update_comments_statistics(increase_blocked_comments=True)

                    raise ValueError(f'following fields contains offensive language: {failed_fields}')
            except ValueError as _e:
                raise ValueError(_e.args[0])
            except ResourceExhausted:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AI_REQUEST_QUOTA_EXCEEDED)
            except Exception as _e:
                logger = get_logger()
                logger.error(_e, exc_info=True)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AI_VALIDATION_ERROR)
        return self


class CommentUpdateSchema(CommentBaseSchema):
    text: Optional[str] = Field(default=None, example='some text', min_length=3, max_length=1000)


class CommentCreateSchema(CommentBaseSchema):
    post_id: PyObjectId
    author_id: PyObjectId
    post_author_answer: bool = False
    answered_comment_id: Optional[PyObjectId] = Field(default=None)


class CommentReadSchema(CommentBaseSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    author_id: PyObjectId
    post_id: PyObjectId
    post_author_answer: bool = False
    answered_comment_id: Optional[PyObjectId] = Field(default=None)
    updated_at: datetime
    created_at: datetime


class CommentReadPaginationSchema(BaseModel):
    total_items_count: int
    page_size: int
    page: int
    items: List[CommentReadSchema] = []


class CommentStatisticsSchema(BaseModel):
    blocked_comments: int = 0
    created_comments: int = 0
    date: datetime

    @field_serializer('date')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%d")


class CommentStatisticsResponseSchema(BaseModel):
    items: List
