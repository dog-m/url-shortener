from fastapi import APIRouter

from .auth import api_auth_router
from .user import api_user_router

#

api_router = APIRouter(prefix='/api/v1', tags=['api'])

api_router.include_router(api_auth_router)
api_router.include_router(api_user_router)

