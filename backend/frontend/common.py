from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

#

frontend_files     = StaticFiles(directory='./frontend', html=False)
frontend_templates = Jinja2Templates(directory='./frontend')

