from fastapi import Request, Response, status
from fastapi.responses import HTMLResponse
from slowapi.errors import RateLimitExceeded

#



RATE_LIMITER_DEFAULT_RESPONSE = '''
<!DOCTYPE html>
<html>
    <head><title>429 - Too Many Requests</title></head>
    <body><h1>Too Many Requests</h1></body>
</html>
'''


def rate_limit_exceeded_handler(request: Request, _: RateLimitExceeded) -> Response:
    response = HTMLResponse(
        content=RATE_LIMITER_DEFAULT_RESPONSE,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response

