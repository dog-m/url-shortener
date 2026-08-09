from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.api.urls_primary import api_urls_router
from backend.api.v1 import api_router
from backend.core.caching import clear_caches, init_caches
from backend.core.exceptions import rate_limit_exceeded_handler
from backend.core.security import limiter
from backend.db.database import init_db
from backend.frontend import (
    frontend_index_router,
    frontend_seo_router,
    frontend_user_router,
    not_found_error_handler,
)
from backend.models.click import ClickEvent
from backend.models.url import Url
from backend.models.user import User
from backend.services.user import upsert_primary_superuser

#


async def on_startup(app: FastAPI) -> None:  # noqa: ARG001
    # TODO: this is no longer needed since I have no service layer yet (but still left here to create tables)
    _ = (User, Url, ClickEvent)
    await init_db()
    await init_caches()
    #
    await upsert_primary_superuser()


async def on_shutdown(app: FastAPI) -> None:  # noqa: ARG001
    await clear_caches()



@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup(app)
    try:
        #logger.info('Startup completed')
        yield
    finally:
        await on_shutdown(app)


app = FastAPI(
    title='URL Shortener service',
    description='A description ?',
    version='1.0',
    lifespan=lifespan,
)
app.state.limiter = limiter

# container-related handler
@app.get('/health')
async def health_check():
    return {
        'status': 'healthy',
    }



# frontend routes
app.include_router(frontend_index_router)
app.include_router(frontend_seo_router)
app.include_router(frontend_user_router)

# api routes
app.include_router(api_urls_router)
app.include_router(api_router)

# misc routes
app.mount('/static', StaticFiles(directory='static'), name='static')

# errors
app.add_exception_handler(status.HTTP_404_NOT_FOUND, not_found_error_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# application-wide middleware stack (order matters)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
#app.add_middleware(RequestLimiter, cache=DefaultRateLimiterCache())  # custom rate limiter (unused)
app.add_middleware(SlowAPIMiddleware)

