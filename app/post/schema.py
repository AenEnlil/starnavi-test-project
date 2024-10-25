from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.custom_fields import PyObjectId


class PostBaseSchema(BaseModel):
    title: str
    text: str


class PostCreateInSchema(BaseModel):
    title: str
    text: str


class PostCreateSchema(PostCreateInSchema):
    user_id: PyObjectId


class PostUpdateSchema(PostBaseSchema):
    title: Optional[str] = Field(default=None, example='Post')
    text: Optional[str] = Field(default=None, example='some text')


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



