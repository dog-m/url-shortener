from fastapi.staticfiles import StaticFiles

#

frontend_files  = StaticFiles(directory='./frontend', html=False)
