"""
Notification System
"""

from src.config import config
from src.logger import logger
from telegram import Bot

class NotificationHandler:
    """Sends notifications via Telegram"""
    
    async def send_notification(self, message):
        """Send notification to Telegram chat"""
        try:
            bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"✅ Notification sent")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

notifier = NotificationHandler()
