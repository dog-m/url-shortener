from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.frontend.common import frontend_files

#



async def not_found_error_handler(request: Request, e: Exception) -> Response:  # noqa: ARG001
    res = await frontend_files.get_response('404.html', request.scope)
    res.status_code = status.HTTP_404_NOT_FOUND
    return res




ERROR_MESSAGES = {
    'value_error.email': {
        'en': 'Invalid email format',
        'fr': 'Format de courriel invalide',
    }
}
ERROR_MESSAGE_LANGS = set(ERROR_MESSAGES['value_error.email'].keys())


async def validation_exception_handler(request: Request, e: RequestValidationError):
    # 2. Determine the user's language (usually from the 'Accept-Language' header)
    lang = request.headers.get('accept-language', 'en').split(',')[0][:2]
    if lang not in ERROR_MESSAGE_LANGS:
        lang = 'en'

    errors = []
    for error in e.errors():
        # Pydantic error types are found in error['type']
        err_type = error['type']

        # If we have a translation, use it. Otherwise, use a default.
        if translations := ERROR_MESSAGES.get(err_type):
            msg = translations.get(lang, translations['en'])
        else:
            msg = 'Validation error'

        errors.append({
            'field': error['loc'][-1],
            'message': msg
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'errors': errors
        },
    )
