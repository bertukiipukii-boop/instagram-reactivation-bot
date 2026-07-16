"""
Database System
"""

import aiosqlite
from src.logger import logger

class Database:
    """Simple database for account tracking"""
    
    def __init__(self, db_path="data/accounts.db"):
        self.db_path = db_path
        self.conn = None
    
    async def init(self):
        """Initialize database"""
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                status TEXT,
                followers INTEGER,
                last_checked TIMESTAMP
            )
        """)
        await self.conn.commit()
        logger.info("✅ Database initialized")
    
    async def get_all_accounts(self):
        """Get all accounts"""
        cursor = await self.conn.execute("SELECT username, status FROM accounts")
        return await cursor.fetchall()
    
    async def get_account_status(self, username):
        """Get account status"""
        cursor = await self.conn.execute(
            "SELECT status, followers, last_checked FROM accounts WHERE username = ?",
            (username,)
        )
        return await cursor.fetchone()

db = Database()
