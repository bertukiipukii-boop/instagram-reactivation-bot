"""
Telegram Bot Handler
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config import config
from src.logger import logger
from src.monitoring import monitor
from datetime import datetime

class TelegramBotHandler:
    """Handles all Telegram bot commands"""
    
    def __init__(self):
        self.app = None
        self.start_time = datetime.now()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        message = """
👋 <b>Welcome to Instagram Monitor Bot!</b>

I monitor Instagram accounts 24/7 and notify you when they change status.

Use /help to see all commands.
"""
        await update.message.reply_html(message)
        logger.info(f"User {user.first_name} started bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """
📚 <b>Available Commands:</b>

/start - Welcome message
/help - Show this help message
/ping - Check if bot is alive
/add - Add Instagram account to monitor
/remove - Stop monitoring an account
/list - Show all monitored accounts
/status - Check account status

<b>Examples:</b>
/add cristiano
/add messi
/list
/status cristiano
"""
        await update.message.reply_html(message)
        logger.info("Help command requested")
    
    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ping command"""
        await update.message.reply_text("🏓 Pong! Bot is alive!")
        logger.info("Ping command received")
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command"""
        logger.info(f"Add command received. Args: {context.args}")
        
        if not context.args:
            await update.message.reply_text("❌ Please provide username.\nExample: /add cristiano")
            return
        
        username = context.args[0].lower().strip('@')
        await monitor.add_account(username)
        await update.message.reply_html(f"✅ <b>@{username}</b> added to monitoring!")
        logger.info(f"Added account: {username}")
    
    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove command"""
        logger.info(f"Remove command received. Args: {context.args}")
        
        if not context.args:
            await update.message.reply_text("❌ Please provide username.\nExample: /remove cristiano")
            return
        
        username = context.args[0].lower().strip('@')
        await monitor.remove_account(username)
        await update.message.reply_html(f"✅ Stopped monitoring <b>@{username}</b>")
        logger.info(f"Removed account: {username}")
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        logger.info("List command received")
        
        if not monitor.accounts:
            await update.message.reply_html("📭 No accounts being monitored")
            return
        
        message = "<b>📋 Monitored Accounts:</b>\n\n"
        for i, (username, data) in enumerate(monitor.accounts.items(), 1):
            status = data.get("last_status", "❓")
            message += f"{i}. @{username} - {status}\n"
        
        await update.message.reply_html(message)
        logger.info("List command sent")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        logger.info(f"Status command received. Args: {context.args}")
        
        if not context.args:
            await update.message.reply_text("❌ Please provide username.\nExample: /status cristiano")
            return
        
        username = context.args[0].lower().strip('@')
        
        if username not in monitor.accounts:
            await update.message.reply_html(f"❌ <b>@{username}</b> not in monitoring list")
            return
        
        data = monitor.accounts[username]
        status = data.get("last_status", "❓")
        last_checked = data.get("last_checked", "Never")
        
        message = f"""
<b>📊 Status for @{username}:</b>

Status: {status}
Last checked: {last_checked}
"""
        await update.message.reply_html(message)
        logger.info(f"Status check for {username}")
    
    async def setup(self):
        """Setup the bot"""
        logger.info("Setting up Telegram bot...")
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Add all command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("ping", self.ping_command))
        self.app.add_handler(CommandHandler("add", self.add_command))
        self.app.add_handler(CommandHandler("remove", self.remove_command))
        self.app.add_handler(CommandHandler("list", self.list_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        
        logger.info("✅ All command handlers registered")
    
    async def start_polling(self):
        """Start polling"""
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(allowed_updates=[])
            logger.info("✅ Bot polling started")
        except Exception as e:
            logger.error(f"Error starting polling: {e}")
            raise
    
    async def stop_polling(self):
        """Stop polling"""
        try:
            if self.app:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
            logger.info("✅ Bot stopped")
        except Exception as e:
            logger.warning(f"Error stopping: {e}")

bot_handler = TelegramBotHandler()
