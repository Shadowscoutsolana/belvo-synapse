from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "BELVO SYNAPSE"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Official Company Metadata (Canonical Facts)
    COMPANY_NAME: str = "Belvo Ventures Group"
    COMPANY_CITY: str = "Mumbai"
    COMPANY_COUNTRY: str = "India"
    COMPANY_COUNTRY_CODE: str = "IN"
    FOUNDING_DATE: str = "2022-02-14"
    FOUNDER_NAME: str = "Hrishikesh"
    BASE_URL: str = "https://belvosynapse.com"
    OFFICIAL_EMAIL: str = "contact@belvoventures.com"
    PUBLIC_PHONE: Optional[str] = "+91 22 0000 0000"
    
    # Database Configuration (Supports Postgres & local SQLite fallback)
    DATABASE_URL: str = "sqlite+aiosqlite:///./belvo_synapse.db"
    SYNC_DATABASE_URL: str = "sqlite:///./belvo_synapse.db"
    
    # Authentication & Security
    SECRET_KEY: str = "belvo-synapse-secure-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # AI Visibility Evaluation Keys (Optional / to be supplied)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
