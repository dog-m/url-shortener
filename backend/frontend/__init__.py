from fastapi import APIRouter

from .admin import router as routes_admin
from .index import router as routes_index
from .seo import router as routes_seo
from .urls import router as routes_urls
from .user import router as routes_user

#


frontend_router = APIRouter(tags=['frontend'], include_in_schema=False)

frontend_router.include_router(routes_admin)
frontend_router.include_router(routes_index)
frontend_router.include_router(routes_seo)
frontend_router.include_router(routes_urls)
frontend_router.include_router(routes_user)

