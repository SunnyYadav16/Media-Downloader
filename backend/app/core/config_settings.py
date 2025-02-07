import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class.
    """

    ALLOWED_ORIGINS: List[str]
    ALLOW_CREDENTIALS: bool
    ALLOW_METHODS: List[str]
    ALLOW_HEADERS: List[str]
    APP_DEBUG: bool
    S3_BUCKET_NAME: str
    AWS_ACCESS_KEY_ID_VALUE: str
    AWS_SECRET_ACCESS_KEY_VALUE: str

    class Config:
        """
        Config class.
        """
        if os.path.exists(".env"):
            env_file = ".env"
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings():
    """
    Config settings function.
    """
    return Settings()


settings = get_settings()
