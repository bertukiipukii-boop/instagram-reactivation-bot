"""
Configuration Manager
Reads .env file and provides configuration settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Main configuration class"""
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Instagram Settings
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
    
    # Monitoring Settings
    MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "300"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "10"))
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DB_PATH = "data/monitoring.db"
    
    # Validation
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in .env file")
        if not Config.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID not set in .env file")
        return True

# Create config instance
config = Config()
