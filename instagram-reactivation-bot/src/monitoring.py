"""
Instagram Account Monitoring System
"""

import asyncio
from src.logger import logger
from src.database import db
from src.notifications import notifier
from instagrapi import Client
import time

class InstagramMonitor:
    """Monitors Instagram accounts for status changes"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 1  # Check every 1 second
        self.accounts = {}
    
    async def add_account(self, username):
        """Add account to monitor"""
        if username in self.accounts:
            logger.info(f"Account {username} already monitored")
            return False
        
        self.accounts[username] = {
            "last_status": None,
            "last_checked": None
        }
        logger.info(f"✅ Added account to monitoring: {username}")
        return True
    
    async def remove_account(self, username):
        """Remove account from monitoring"""
        if username in self.accounts:
            del self.accounts[username]
            logger.info(f"✅ Removed account from monitoring: {username}")
        return True
    
    async def check_account_status(self, username):
        """Check if Instagram account is active or unavailable"""
        try:
            client = Client()
            
            # Try to get user info
            try:
                user_info = client.user_info_by_username(username)
                status = "ACTIVE"
                followers = user_info.follower_count
                logger.info(f"✅ {username}: {status} ({followers} followers)")
                return status, followers
            
            except Exception as e:
                error_str = str(e).lower()
                
                if "not found" in error_str or "user not found" in error_str:
                    status = "UNAVAILABLE"
                elif "suspended" in error_str or "action blocked" in error_str:
                    status = "SUSPENDED"
                else:
                    status = "UNKNOWN"
                
                logger.warning(f"⚠️ {username}: {status}")
                return status, 0
        
        except Exception as e:
            logger.error(f"Error checking {username}: {e}")
            return "UNKNOWN", 0
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting monitor loop...")
        
        while self.running:
            try:
                if not self.accounts:
                    logger.debug("No accounts to monitor")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                logger.info(f"📊 Checking {len(self.accounts)} accounts...")
                
                for username in list(self.accounts.keys()):
                    try:
                        status, followers = await self.check_account_status(username)
                        
                        # Check if status changed
                        old_status = self.accounts[username]["last_status"]
                        if old_status and status != old_status:
                            logger.info(f"🔔 Status changed: {username} {old_status} -> {status}")
                            await notifier.send_notification(
                                f"🔔 {username}\n{old_status} → {status}"
                            )
                        
                        # Update account info
                        self.accounts[username]["last_status"] = status
                        self.accounts[username]["last_checked"] = time.time()
                    
                    except Exception as e:
                        logger.error(f"Error monitoring {username}: {e}")
                
                logger.info(f"✅ Check complete. Waiting {self.check_interval}s...")
                await asyncio.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """Start monitoring"""
        self.running = True
        logger.info("🚀 Monitor started")
        await self.monitor_loop()
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("🛑 Monitor stopped")

# Create monitor instance
monitor = InstagramMonitor()
