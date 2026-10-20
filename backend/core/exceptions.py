from fastapi import Request, Response, status
from fastapi.responses import HTMLResponse

#


RATE_LIMITER_DEFAULT_RESPONSE = '''
<!DOCTYPE html>
<html>
    <head><title>429 - Too Many Requests</title></head>
    <body><h1>Too Many Requests</h1></body>
</html>
'''


def rate_limit_exceeded_handler(request: Request, _: Exception) -> Response:
    response = HTMLResponse(
        content=RATE_LIMITER_DEFAULT_RESPONSE,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response  # type: ignore


def access_control_handler(request: Request, _: Exception) -> Response:  # noqa: ARG001
    return Response(
        content='Unauthorized',
        status_code=status.HTTP_401_UNAUTHORIZED,
        media_type='text/plain',
    )


def insufficient_privileges_handler(request: Request, _: Exception) -> Response:  # noqa: ARG001
    return Response(
        content='Forbidden',
        status_code=status.HTTP_403_FORBIDDEN,
        media_type='text/plain',
    )


def concurrent_update_handler(request: Request, _: Exception) -> Response:  # noqa: ARG001
    return Response(
        content='Conflict',
        status_code=status.HTTP_409_CONFLICT,
        media_type='text/plain',
    )
