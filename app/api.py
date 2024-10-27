from fastapi import APIRouter

from app.auth import router as auth_router
from app.post import router as post_router
from app.comments import router as comment_router
from app.user import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router.router)
api_router.include_router(post_router.router)
api_router.include_router(comment_router.router)
api_router.include_router(comment_router.statistics_router)
api_router.include_router(user_router.router)
