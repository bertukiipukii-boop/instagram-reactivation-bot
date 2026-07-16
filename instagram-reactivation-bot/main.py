"""
Instagram Reactivation Monitor Bot - Main Entry Point
"""

import asyncio
import signal
from src.config import config
from src.logger import logger
from src.monitoring import monitor
from src.database import db
from src.telegram_bot import bot_handler

class BotManager:
    """Manages bot lifecycle"""
    
    def __init__(self):
        self.running = True
    
    async def startup(self):
        """Initialize and start the bot"""
        logger.info("=" * 50)
        logger.info("🤖 Instagram Reactivation Monitor Bot")
        logger.info("=" * 50)
        
        # Validate configuration
        try:
            config.validate()
            logger.info("✅ Configuration validated")
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            raise
        
        # Initialize database
        await db.init()
        
        # Setup Telegram bot
        await bot_handler.setup()
        
        # Create tasks
        monitor_task = asyncio.create_task(monitor.start())
        bot_task = asyncio.create_task(bot_handler.start_polling())
        
        logger.info("✅ Bot started successfully")
        
        return monitor_task, bot_task
    
    async def shutdown(self):
        """Shutdown gracefully"""
        logger.info("🛑 Shutting down...")
        await monitor.stop()
        await bot_handler.stop_polling()
        logger.info("✅ Shutdown complete")
    
    def handle_signal(self, signum, frame):
        """Handle signals"""
        logger.info(f"Signal {signum} received")
        self.running = False
    
    async def run(self):
        """Main run loop"""
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        try:
            monitor_task, bot_task = await self.startup()
            
            while self.running:
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.shutdown()

async def main():
    """Main function"""
    manager = BotManager()
    await manager.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
