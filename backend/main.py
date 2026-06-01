from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.frontend import frontend_router
from backend.api.urls import url_router
from backend.db.database import init_db
from backend.models.url import URL
from backend.models.user import User

#

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan handler."""
    # startup
    _ = (User, URL, )  # TODO: this is no longer needed since I have no service layer yet (but still left here to create tables)
    init_db()

    yield

    # shutdown
    pass


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

