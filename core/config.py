from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API
    base_url: str = Field(
        default="https://apimocker.com",
        description="Base URL for apimocker.com",
    )
    request_timeout: int = Field(
        default=10,
        description="HTTP request timeout in seconds",
    )

    # Logging
    log_level: str = Field(default="DEBUG")
    log_file: str = Field(default="logs/test_run.log")
    log_rotation: str = Field(default="10 MB")


settings = Settings()
