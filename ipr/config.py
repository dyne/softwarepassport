from pydantic import BaseSettings, HttpUrl, IPvAnyAddress, RedisDsn


class Settings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost:8000,http://localhost:3000"
    DATABASE_URL: str = "sqlite:///./licenses.db"
    HOST: IPvAnyAddress = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    SAWROOM: HttpUrl = "https://apiroom.net/api/zenbridge/sawroom-write"
    FABRIC: HttpUrl = "https://apiroom.net/api/zenbridge/fabric-write"
    PAGINATION_WINDOW: int = 100
    CELERY_BROKER: RedisDsn = "redis://127.0.0.1:6379/0"
    CELERY_BACKEND: RedisDsn = "redis://127.0.0.1:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
