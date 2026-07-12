import secrets
from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

#


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore',
    )

    # common info
    debug: bool    = Field(default=False, description='Debug mode')
    log_level: str = Field(default='INFO', description='Logging level')

    # db info
    database_url: str = Field(
        default='sqlite+aiosqlite:///./url_shortener.db',
        description='Database connection URL',
    )

    # CORS info
    cors_origins: list[str] = Field(default=['*'], description='Allowed CORS origins')

    # caching
    redis_url: str | None    = Field(default=None, description='Redis connection URL')
    cache_ttl: int           = Field(default=3600, description='Default cache entry TLL')
    cache_status_header: str = Field(default='X-FastAPI-Cache', description='Status header for cached responses')

    # JWT info
    jwt_secret_key: str                  = Field(default=secrets.token_urlsafe(32), description='JWT secret key')
    jwt_algorithm: str                   = Field(default='HS256', description='JWT algorithm')  # HMAC with SHA-256
    jwt_access_token_expire_minutes: int = Field(default=10, description='JWT access token expiration')
    jwt_refresh_token_expire_days: int   = Field(default=30, description='JWT refresh token expiration')


settings = Settings()

