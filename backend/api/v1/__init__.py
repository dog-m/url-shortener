from fastapi import APIRouter

from .auth import router as routes_auth
from .urls import router as routes_urls
from .user import router as routes_user

#

api_router = APIRouter(prefix='/api/v1', tags=['api'])

api_router.include_router(routes_auth)
api_router.include_router(routes_urls)
api_router.include_router(routes_user)

