# ============================================
# INSTAGRAM MONITORING BOT - CONFIGURATION
# ============================================

# 🔑 DISCORD BOT TOKEN
# Paste your bot token here (from Discord Developer Portal)
DISCORD_TOKEN = "MTUyNjUyOTE1MTY4NTg4NjAyMg.GjLJzz.DRS1dDsg7t2V7uvso8vuh36btjvMjcOHkg_kc4"

# 📢 DISCORD SETTINGS
NOTIFICATION_CHANNEL_ID = 526508456792821814  # Put your channel ID here (right-click channel > Copy ID)
ADMIN_ROLE_NAME = "Admin"     # Only admins can use commands

# ⏱️ MONITORING SETTINGS
CHECK_INTERVAL = 300  # Check every 300 seconds (5 minutes)
INITIAL_RETRY_DELAY = 10  # Retry failed checks after 10 seconds
MAX_RETRIES = 3  # Try 3 times before giving up

# 🎨 EMBED COLORS (RGB values converted to hex)
COLOR_SUCCESS = 0x00FF00  # Green - Account is available
COLOR_ERROR = 0xFF0000   # Red - Error occurred
COLOR_INFO = 0x0000FF   # Blue - Info/Status
COLOR_WARNING = 0xFFA500  # Orange - Warning

# 📊 DATABASE
DATABASE_FILE = "monitor.db"
LOG_FILE = "bot.log"

# 🤖 BOT PREFIX
BOT_PREFIX = "!"

# 🔄 INSTAGRAM SETTINGS
INSTAGRAM_TIMEOUT = 30  # Wait max 30 seconds for Instagram response
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 📝 STATUS MESSAGES
STATUS_AVAILABLE = "available"
STATUS_UNAVAILABLE = "unavailable"
STATUS_ERROR = "error"
