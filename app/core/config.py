import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = os.getenv("ENV_FILE", ".env.local")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_ignore_empty=True)
    ENVIRONMENT: str = "local"
    HOST: str = "0.0.0.0"
    PORT: str = "8081"
    DATABASE_URL: str = "sqlite:///./todo.db"
    JWT_SECRET_KEY: str = "insecure-dev-secret-override-in-env"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    # No user table yet — a single demo account issues tokens, stored as
    # hashes so no plaintext credential sits in config/env. Swap for a real
    # user lookup once persistence is added. Defaults below hash to
    # username "admin" / password "changeme" — override both in .env.
    DEMO_USERNAME_HASH: str = (
        "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    )
    DEMO_PASSWORD_HASH: str = (
        "$2b$12$0gbkjlfhPIcyUs6pDDmSpugThlWl8r7ZIAbItlcuSvLkwgZnxVAmC"
    )
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://example.com"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
