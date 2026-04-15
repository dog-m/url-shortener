from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
async def root():
    return FileResponse('./frontend/index.html', media_type="text/html")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./frontend/favicon.png', media_type="image/png")
