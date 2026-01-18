#!/usr/bin/env python3
"""
Development runner with Textual dev features enabled
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set dev mode environment
os.environ['TEXTUAL'] = 'devtools'

# Import and run
from src.ui import TradingTerminalApp
from src.config import Config
import logging

def setup_logging():
    """Setup logging configuration"""
    Config.LOGS_DIR.mkdir(exist_ok=True)
    log_file = Config.LOGS_DIR / "trader.log"

    logging.basicConfig(
        level=logging.DEBUG,  # More verbose in dev mode
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

if __name__ == "__main__":
    setup_logging()
    print("🚀 Starting Trading Terminal in DEV mode...")
    print("📝 Logs: logs/trader.log")
    print("⚙️  Config: .env")
    print("")

    app = TradingTerminalApp()
    app.run()
