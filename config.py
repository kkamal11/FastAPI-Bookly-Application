from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    DATABASE_URL: str
    ECHO_SQL: bool = False
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    DEBUG: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    JTI_EXPIRY_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    ) 

env_config = Settings()