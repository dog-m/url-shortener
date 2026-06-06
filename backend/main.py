from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.urls import url_router
from backend.core.caching import clear_caches, init_caches
from backend.db.database import init_db
from backend.frontend.pages import frontend_router
from backend.models.click import ClickEventDto
from backend.models.url import UrlDto
from backend.models.user import UserDto

#


async def on_startup(app: FastAPI) -> None:  # noqa: ARG001
    # TODO: this is no longer needed since I have no service layer yet (but still left here to create tables)
    _ = (UserDto, UrlDto, ClickEventDto)
    await init_db()
    await init_caches()


async def on_shutdown(app: FastAPI) -> None:  # noqa: ARG001
    await clear_caches()



@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup(app)
    yield
    await on_shutdown(app)


app = FastAPI(
    title='URL Shortener service',
    description='A description ?',
    version='1.0',
    lifespan=lifespan,
)


# routers
app.include_router(frontend_router)
app.include_router(url_router)
app.mount('/static', StaticFiles(directory='static'), name='static')


# container-related handler
@app.get('/health')
async def health_check():
    return {
        'status': 'healthy',
    }

