from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.custom_fields import PyObjectId


class CommentBaseSchema(BaseModel):
    text: str


class CommentCreateInSchema(BaseModel):
    text: str


class CommentUpdateSchema(CommentBaseSchema):
    text: Optional[str] = Field(default=None, example='some text')


class CommentCreateSchema(CommentCreateInSchema):
    post_id: PyObjectId
    author_id: PyObjectId
    updated_at: datetime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    created_at: datetime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class CommentReadSchema(CommentBaseSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    author_id: PyObjectId
    post_id: PyObjectId
    updated_at: datetime
    created_at: datetime
