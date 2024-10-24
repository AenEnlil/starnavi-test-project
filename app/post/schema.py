from datetime import datetime
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
    created_at: datetime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class PostReadSchema(PostBaseSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    user_id: PyObjectId
    created_at: datetime




