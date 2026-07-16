"""
Logging Configuration
Provides colored logging for the bot
"""

import logging
import colorlog
import os
from src.config import config

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def setup_logger(name):
    """Setup and return a logger instance"""
    
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    
    # File handler (no colors)
    file_handler = logging.FileHandler("logs/bot.log")
    file_handler.setLevel(config.LOG_LEVEL)
    
    # Colored formatter for console
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s]%(reset)s %(levelname)-8s %(blue)s%(name)s%(reset)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Plain formatter for file
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create main logger
logger = setup_logger("InstagramBot")
