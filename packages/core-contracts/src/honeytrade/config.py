from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
import structlog
import os

logger = structlog.get_logger()

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", env="ENVIRONMENT"
    )
    DEBUG: bool = Field(default=False)

    # Alpaca
    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    ALPACA_BASE_URL: str = Field(default="https://paper-api.alpaca.markets")

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: int

    # Machine ID (Hardware Lock)
    MACHINE_ID: str = Field(default_factory=lambda: os.getenv("MACHINE_ID", "default-machine-id"))

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @field_validator("ALPACA_API_KEY", "ALPACA_SECRET_KEY", "TELEGRAM_BOT_TOKEN")
    @classmethod
    def validate_secrets(cls, v: str, info) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError(f"{info.field_name} çok kısa veya boş!")
        return v.strip()

    def print_banner(self):
        logger.info("🚀 HoneyTrade Equities starting...", 
                    env=self.ENVIRONMENT,
                    machine_id=self.MACHINE_ID[:8] + "...")


# Global config instance
config: AppConfig = AppConfig()