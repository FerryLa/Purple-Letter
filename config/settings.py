"""
Purple Letter Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "Purple Letter API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./data/purple_letter.db"

    # News Scanner Core Path
    NEWS_SCANNER_CORE_PATH: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "News-Leafletter")
    )
    NEWS_SCANNER_DB_PATH: Optional[str] = None  # Auto-detected from core

    # Scoring Weights (ImpactScore formula)
    WEIGHT_MARKET_RELEVANCE: float = 1.0
    WEIGHT_BUSINESS_RELEVANCE: float = 1.0
    WEIGHT_TECH_SHIFT: float = 1.0
    WEIGHT_URGENCY: float = 1.0

    # Recommendation Settings
    DEFAULT_TOP_N: int = 4
    MIN_IMPACT_SCORE: int = 4

    # Power BI Settings
    POWERBI_REFRESH_INTERVAL: int = 300  # seconds

    # CORS Settings
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
