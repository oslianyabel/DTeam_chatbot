import logging
from typing import Optional

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class EnvConfig(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"

    ENVIRONMENT: Optional[str] = None

    AVANGENIO_API_KEY: Optional[str] = None

    EMAIL: Optional[str] = None
    MY_EMAIL: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_HOST: Optional[str] = None


config = EnvConfig()

if __name__ == "__main__":
    print(config.AVANGENIO_API_KEY)
