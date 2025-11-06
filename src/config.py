"""Configuration management for trading terminal"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # API Configuration
    BINGX_API_KEY: str = os.getenv("BINGX_API_KEY", "")
    BINGX_API_SECRET: str = os.getenv("BINGX_API_SECRET", "")

    # Trading Configuration
    DEFAULT_LEVERAGE: int = int(os.getenv("DEFAULT_LEVERAGE", "5"))
    TESTNET: bool = os.getenv("TESTNET", "false").lower() == "true"

    # Directory Configuration
    BASE_DIR: Path = Path(__file__).parent.parent
    TRADES_DIR: Path = BASE_DIR / "trades"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Position Management
    SL_OFFSET_PERCENT: float = 0.1  # 0.1% above entry/TP when moving SL

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.BINGX_API_KEY or not cls.BINGX_API_SECRET:
            raise ValueError("BingX API credentials not configured. Check .env file")
        return True

    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        cls.TRADES_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)


# Ensure directories exist on import
Config.ensure_directories()
