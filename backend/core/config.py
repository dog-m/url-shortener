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
        default='postgresql+psycopg://postgres:postgres@localhost:5432/url_shortener',
        description='Database connection URL',
    )

    # CORS info
    cors_origins: list[str] = Field(default=['*'], description='Allowed CORS origins')



@lru_cache(maxsize=1)  # awkward Singleton
def get_settings() -> Settings:
    return Settings()

