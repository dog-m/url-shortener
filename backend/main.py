from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./static/favicon.ico')
