import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = os.getenv("ENV_FILE", ".env.local")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_ignore_empty=True)
    ENVIRONMENT: str = "local"
    HOST: str = "0.0.0.0"
    PORT: str = "8081"
    DATABASE_URL: str = "sqlite:///./todo.db"


settings = Settings()
