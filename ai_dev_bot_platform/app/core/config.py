from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Any, Optional


class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None  # Will be constructed if not provided

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    TELEGRAM_BOT_TOKEN: str

    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

    API_KEY_ENCRYPTION_KEY: (
        str  # For encrypting any keys stored in DB (not external provider keys)
    )

    # Model Configuration
    ARCHITECT_MODEL: str = "deepseek/deepseek-r1-0528:free"
    IMPLEMENTER_MODEL: str = "tngtech/deepseek-r1t-chimera:free"
    VERIFICATION_MODEL: str = "deepseek/deepseek-r1-0528:free"
    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"

    PLATFORM_CREDIT_VALUE_USD: float = 0.01
    MARKUP_FACTOR: float = 1.5

    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    MOCK_STRIPE_PAYMENTS: bool = False
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    WEBAPP_URL: str = "http://localhost:8000"

    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # API Key Pools for round-robin (loaded from env or defaults)
    # Example: GOOGLE_API_KEY_POOL='key1,key2'
    # Example: OPENROUTER_API_KEY_POOL='keyA,keyB'
    # These will be parsed into lists by the APIKeyManager
    # For simplicity, we'll start with single keys from above first.

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
