#!/usr/bin/env python3
"""
JSON API Trader - Automated Trading Terminal
Main entry point
"""
import asyncio
import logging
from pathlib import Path
from src.ui import TradingTerminalApp
from src.config import Config


def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    Config.LOGS_DIR.mkdir(exist_ok=True)

    # Configure logging
    log_file = Config.LOGS_DIR / "trader.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Suppress noisy libraries
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠ Warning: .env file not found")
        print("Please create .env file with your BingX API credentials")
        print("See .env.example for template")
        return

    # Run the terminal app
    app = TradingTerminalApp()
    app.run()


if __name__ == "__main__":
    main()
