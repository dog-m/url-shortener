import secrets
from datetime import UTC, datetime, timedelta

import jwt

from backend.core.config import settings

#


def create_access_token(data: dict) -> str:
    data = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    data.update({
        'exp': expire,
        'type': 'access',
        'jti': secrets.token_urlsafe(32),
    })

    return jwt.encode(
        data, settings.jwt_secret_key, settings.jwt_algorithm
    )



def create_refresh_token(data: dict[str, object]) -> str:
    data = data.copy()

    expire = datetime.now(UTC) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )

    data.update({
        'exp': expire,
        'type': 'refresh',
        'jti': secrets.token_urlsafe(32),
    })

    return jwt.encode(
        data, settings.jwt_secret_key, settings.jwt_algorithm
    )



def verify_token(token: str) -> dict[str, object]:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        if payload.get('type') is None:
            raise jwt.InvalidTokenError('Missing token type')

        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token has expired')
    except jwt.PyJWTError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {e!s}")



def get_current_user_id(token: str) -> str:
    if (user_id := verify_token(token).get('sub')) is not None:
        return user_id
    else:
        raise jwt.InvalidTokenError('Missing user ID in token')

