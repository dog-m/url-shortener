from pydantic import BaseModel

#


class ApiOk(BaseModel):
    status: str = 'ok'


class ApiError(BaseModel):
    status: str = 'error'
    msg: str
    code: int | None = None

