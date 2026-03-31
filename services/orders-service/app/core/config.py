from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database — required, no default intentionally
    database_url: str

    # JWT — shared secret with auth-service; required, no default intentionally
    jwt_secret: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300  # 5 minutes

    # AI (optional)
    anthropic_api_key: str | None = None

    # Application
    env: str = "development"
    log_level: str = "INFO"


settings = Settings()  # type: ignore[call-arg]
