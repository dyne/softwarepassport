from typing import Optional, Dict, Any
from pydantic import (
    BaseSettings,
    HttpUrl,
    IPvAnyAddress,
    RedisDsn,
    PostgresDsn,
    validator,
)


class Settings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost:8000,http://localhost:3000"
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    # DATABASE_URL: Optional[str] = "sqlite:///./projects.db"
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    HOST: IPvAnyAddress = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 14
    SAWROOM: HttpUrl = "https://apiroom.net/api/zenbridge/sawroom-write"
    FABRIC: HttpUrl = "https://apiroom.net/api/zenbridge/fabric-write"
    PAGINATION_WINDOW: int = 100
    CELERY_BROKER: RedisDsn = "redis://127.0.0.1:6379/0"
    CELERY_BACKEND: RedisDsn = "redis://127.0.0.1:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
