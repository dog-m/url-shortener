import html
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import jwt
from pwdlib.hashers import HasherProtocol
from pwdlib.hashers.bcrypt import BcryptHasher
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.core.config import settings

#


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=settings.rate_limits,
    key_style='endpoint',
    strategy='sliding-window-counter',
    storage_uri=settings.redis_url,
    key_prefix='RATE-LIMITER:',
    headers_enabled=True,
)



_SAFE_PROTOCOLS = { 'http', 'https', 'HTTP', 'HTTPS', }

def is_safe_url(url: str) -> bool:
    try:
        return urlparse(url, allow_fragments=False).scheme in _SAFE_PROTOCOLS
    except ValueError:
        return False



def sanitize_html(text: str) -> str:
    return html.escape(text, quote=True)



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



_pwd_hasher: HasherProtocol = BcryptHasher()


def password_get_hash(password: str, salt: str | None = None) -> str:
    return _pwd_hasher.hash(password, salt=salt)


def password_verify(plain_password: str, hashed_password: str) -> bool:
    return _pwd_hasher.verify(plain_password, hashed_password)

