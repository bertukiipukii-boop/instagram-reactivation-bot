"""
Instagram Account Status Checker
Checks if Instagram accounts are active or unavailable
"""

import aiohttp
import asyncio
from src.logger import logger

class InstagramChecker:
    """Check Instagram account status"""
    
    def __init__(self):
        self.base_url = "https://www.instagram.com"
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def check_account(self, username):
        """
        Check if an Instagram account exists and is active
        Returns: (status, followers)
        Status can be: ACTIVE, SUSPENDED, DEACTIVATED, UNAVAILABLE, UNKNOWN
        """
        try:
            url = f"{self.base_url}/{username}/?__a=1&__w=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=headers, allow_redirects=False) as response:
                    
                    # 200 = Account exists and is active
                    if response.status == 200:
                        try:
                            data = await response.json()
                            user = data.get('user', {})
                            followers = user.get('edge_followed_by', {}).get('count', 0)
                            logger.info(f"✅ {username} - ACTIVE ({followers} followers)")
                            return ("ACTIVE", followers)
                        except:
                            return ("ACTIVE", 0)
                    
                    # 404 = Account doesn't exist or is deactivated
                    elif response.status == 404:
                        logger.info(f"❌ {username} - UNAVAILABLE (404)")
                        return ("UNAVAILABLE", 0)
                    
                    # 403 = Account suspended
                    elif response.status == 403:
                        logger.info(f"⚠️ {username} - SUSPENDED (403)")
                        return ("SUSPENDED", 0)
                    
                    # Other status codes
                    else:
                        logger.warning(f"⚠️ {username} - Unknown status ({response.status})")
                        return ("UNKNOWN", 0)
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ {username} - Timeout (no response)")
            return ("UNKNOWN", 0)
        except aiohttp.ClientError as e:
            logger.warning(f"❌ {username} - Error: {str(e)}")
            return ("UNKNOWN", 0)
        except Exception as e:
            logger.error(f"❌ {username} - Unexpected error: {str(e)}")
            return ("UNKNOWN", 0)

# Create checker instance
checker = InstagramChecker()
