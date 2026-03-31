from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://pedidos:pedidos123@localhost:5432/auth_db"

    # JWT — required, no default intentionally
    jwt_secret: str
    access_token_expire_minutes: int = 1440  # 24 hours

    # Application
    env: str = "development"
    log_level: str = "INFO"


settings = Settings()  # type: ignore[call-arg]
