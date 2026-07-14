# ============================================
# INSTAGRAM MONITORING BOT - MAIN FILE
# ============================================

import discord
from discord.ext import commands
import sqlite3
import asyncio
import logging
from datetime import datetime
import instaloader
from config import *

# ============================================
# LOGGING SETUP
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# BOT SETUP
# ============================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# ============================================
# DATABASE SETUP
# ============================================
def init_database():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitored_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            added_by TEXT NOT NULL,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'unknown',
            last_checked TIMESTAMP,
            available INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS check_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

# ============================================
# HELPER FUNCTIONS
# ============================================

def check_instagram_username(username):
    """Check if Instagram username is available"""
    try:
        L = instaloader.Instaloader()
        try:
            profile = L.get_profile_from_username(username)
            logger.info(f"Username '{username}' is TAKEN")
            return False, None
        except instaloader.exceptions.ProfileNotExistsException:
            logger.info(f"Username '{username}' is AVAILABLE")
            return True, None
    except Exception as e:
        logger.error(f"Error checking {username}: {str(e)}")
        return None, str(e)

def save_to_database(username, status, error_msg=None):
    """Save check result to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE monitored_accounts 
        SET status = ?, last_checked = CURRENT_TIMESTAMP 
        WHERE username = ?
    ''', (status, username))
    
    cursor.execute('''
        INSERT INTO check_history (username, status, error_message) 
        VALUES (?, ?, ?)
    ''', (username, status, error_msg))
    
    conn.commit()
    conn.close()

def get_all_monitored():
    """Get all monitored usernames from database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM monitored_accounts')
    usernames = [row[0] for row in cursor.fetchall()]
    conn.close()
    return usernames

def username_exists(username):
    """Check if username is already being monitored"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM monitored_accounts WHERE username = ?', (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_channel():
    """Get notification channel"""
    return bot.get_channel(NOTIFICATION_CHANNEL_ID)

# ============================================
# BOT EVENTS
# ============================================

@bot.event
async def on_ready():
    """Bot is ready"""
    logger.info(f'Bot logged in as {bot.user}')
    print(f"✅ Bot is online as: {bot.user}")
    
    # Start the monitoring loop
    bot.loop.create_task(monitoring_loop())

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Use `{BOT_PREFIX}help` for commands.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ Error: {str(error)}")

# ============================================
# BOT COMMANDS
# ============================================

@bot.command(name='add', help='Add Instagram username to monitor')
async def add_username(ctx, username):
    """Add a username to monitor"""
    
    # Check if user has admin role
   # admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE_NAME)
  # if admin_role not in ctx.author.roles:
       # await ctx.send(f"❌ You need the `{ADMIN_ROLE_NAME}` role to use this command.")
       # return
    
    # Check if already monitoring
    if username_exists(username):
        await ctx.send(f"⚠️ Already monitoring `{username}`")
        return
    
    # Add to database
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitored_accounts (username, added_by, status) 
        VALUES (?, ?, ?)
    ''', (username, str(ctx.author), 'pending'))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Username Added",
        description=f"Now monitoring: `{username}`",
        color=COLOR_SUCCESS
    )
    embed.add_field(name="Added by", value=ctx.author.mention)
    embed.add_field(name="Status", value="Pending first check")
    embed.set_footer(text=f"Added at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await ctx.send(embed=embed)
    logger.info(f"Added username: {username} (by {ctx.author})")

@bot.command(name='remove', help='Remove Instagram username from monitor')
async def remove_username(ctx, username):
    """Remove a username from monitoring"""
    
    # Check if user has admin role
   # admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE_NAME)
   # if admin_role not in ctx.author.roles:
       # await ctx.send(f"❌ You need the `{ADMIN_ROLE_NAME}` role to use this command.")
       # return
    
    if not username_exists(username):
        await ctx.send(f"❌ Username `{username}` is not being monitored")
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM monitored_accounts WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Username Removed",
        description=f"No longer monitoring: `{username}`",
        color=COLOR_INFO
    )
    await ctx.send(embed=embed)
    logger.info(f"Removed username: {username}")

@bot.command(name='list', help='Show all monitored usernames')
async def list_usernames(ctx):
    """List all monitored usernames"""
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT username, status, last_checked FROM monitored_accounts')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        await ctx.send("📋 No usernames being monitored yet")
        return
    
    embed = discord.Embed(
        title="📋 Monitored Usernames",
        description=f"Total: {len(rows)}",
        color=COLOR_INFO
    )
    
    for username, status, last_checked in rows:
        last_checked_str = last_checked if last_checked else "Never"
        embed.add_field(
            name=f"`{username}`",
            value=f"Status: {status}\nLast checked: {last_checked_str}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='check', help='Manually check if username is available')
async def check_username(ctx, username):
    """Manually check a username"""
    
    # Check if user has admin role
   # admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE_NAME)
   # if admin_role not in ctx.author.roles:
       # await ctx.send(f"❌ You need the `{ADMIN_ROLE_NAME}` role to use this command.")
       # return
    
    embed = discord.Embed(
        title="🔍 Checking Username",
        description=f"Checking: `{username}`...",
        color=COLOR_INFO
    )
    msg = await ctx.send(embed=embed)
    
    available, error = check_instagram_username(username)
    
    if available is None:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Could not check `{username}`\nError: {error}",
            color=COLOR_ERROR
        )
    elif available:
        embed = discord.Embed(
            title="✅ AVAILABLE",
            description=f"Username `{username}` is **AVAILABLE**! 🎉",
            color=COLOR_SUCCESS
        )
    else:
        embed = discord.Embed(
            title="❌ Taken",
            description=f"Username `{username}` is already taken",
            color=COLOR_ERROR
        )
    
    await msg.edit(embed=embed)

@bot.command(name='commands', help='Show all commands')
async def help_command(ctx):
    """Show help for all commands"""
    embed = discord.Embed(
        title="🤖 Instagram Monitor Bot Commands",
        description="Use these commands to control the bot",
        color=COLOR_INFO
    )
    
    embed.add_field(
        name=f"`{BOT_PREFIX}add <username>`",
        value="Add an Instagram username to monitor",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}remove <username>`",
        value="Remove a username from monitoring",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}list`",
        value="Show all monitored usernames",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}check <username>`",
        value="Manually check if a username is available",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}status`",
        value="Show bot status and uptime",
        inline=False
    )
    
    embed.set_footer(text="⚠️ Most commands require Admin role")
    await ctx.send(embed=embed)

@bot.command(name='status', help='Show bot status')
async def status_command(ctx):
    """Show bot status"""
    embed = discord.Embed(
        title="🤖 Bot Status",
        description="Instagram Monitor Bot",
        color=COLOR_INFO
    )
    embed.add_field(name="Status", value="✅ Online", inline=False)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=False)
    embed.add_field(name="Check Interval", value=f"{CHECK_INTERVAL} seconds", inline=False)
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM monitored_accounts')
    count = cursor.fetchone()[0]
    conn.close()
    
    embed.add_field(name="Monitoring", value=f"{count} usernames", inline=False)
    await ctx.send(embed=embed)

# ============================================
# MONITORING LOOP
# ============================================

async def monitoring_loop():
    """Continuously monitor usernames"""
    await bot.wait_until_ready()
    
    logger.info("Starting monitoring loop...")
    
    while not bot.is_closed():
        try:
            usernames = get_all_monitored()
            
            if usernames:
                logger.info(f"Checking {len(usernames)} usernames...")
                
                for username in usernames:
                    try:
                        available, error = check_instagram_username(username)
                        
                        if available is None:
                            save_to_database(username, STATUS_ERROR, error)
                        elif available:
                            save_to_database(username, STATUS_AVAILABLE)
                            
                            # Send notification
                            channel = get_channel()
                            if channel:
                                embed = discord.Embed(
                                    title="🎉 USERNAME AVAILABLE",
                                    description=f"`{username}` is now AVAILABLE on Instagram!",
                                    color=COLOR_SUCCESS
                                )
                                embed.add_field(name="Time", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                embed.add_field(name="Action", value="Grab it quickly! 🚀")
                                await channel.send(embed=embed)
                                logger.info(f"🎉 AVAILABLE: {username}")
                        else:
                            save_to_database(username, STATUS_UNAVAILABLE)
                        
                        await asyncio.sleep(2)  # Small delay between checks
                    
                    except Exception as e:
                        logger.error(f"Error checking {username}: {e}")
                        save_to_database(username, STATUS_ERROR, str(e))
            
            # Wait before next check cycle
            logger.info(f"Next check in {CHECK_INTERVAL} seconds...")
            await asyncio.sleep(CHECK_INTERVAL)
        
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

# ============================================
# RUN BOT
# ============================================

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Run bot
    try:
        logger.info("Starting bot...")
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Error: {e}")
