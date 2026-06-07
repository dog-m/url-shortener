from functools import lru_cache
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
    debug: bool = Field(default=False, description='Debug mode')

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



@lru_cache(maxsize=1)  # awkward Singleton
def get_settings() -> Settings:
    return Settings()

