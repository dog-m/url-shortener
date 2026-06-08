from fastapi import Response
from fastapi.responses import HTMLResponse

#


def new_html_redirector(target_url: str, *, delay_sec: int = 1) -> Response:
    assert delay_sec >= 0

    return HTMLResponse(
        content=f'''<!DOCTYPE html>
        <html>
            <head><meta http-equiv="refresh" content="{delay_sec};url={target_url}" /></head>
            <body></body>
        </html>
        ''',
    )

