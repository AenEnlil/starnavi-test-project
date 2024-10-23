from fastapi import APIRouter

from app.auth import router as auth_router
from app.user import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router.router)
api_router.include_router(user_router.router)
