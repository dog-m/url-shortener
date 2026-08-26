from fastapi import APIRouter

from .admin import frontend_admin_router
from .index import frontend_index_router
from .seo import frontend_seo_router
from .urls import frontend_urls_router
from .user import frontend_user_router

#


frontend_router = APIRouter(tags=['frontend'], include_in_schema=False)

frontend_router.include_router(frontend_admin_router)
frontend_router.include_router(frontend_index_router)
frontend_router.include_router(frontend_seo_router)
frontend_router.include_router(frontend_urls_router)
frontend_router.include_router(frontend_user_router)

