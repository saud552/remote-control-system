#!/usr/bin/env python3
"""
Telegram Bot Runner with Conda Environment
"""

import asyncio
import logging
import sys
import os

# Add conda environment to path
conda_path = "/home/ubuntu/miniconda/envs/tf_env/bin"
if conda_path not in sys.path:
    sys.path.insert(0, conda_path)

from enhanced_telegram_bot import EnhancedTelegramBot, TelegramConfig

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def main():
    """Main function to run the bot"""
    print("🚀 Starting Enhanced Telegram Bot with Conda Environment...")
    
    # Create configuration
    config = TelegramConfig(
        token="7305811865:AAF_PKkBWEUw-QdLg1ee5Xp7oksTG6XGK8c",
        allowed_users=None,  # Allow all users
        admin_users=[985612253],
        debug=True
    )
    
    # Create and run bot
    bot = EnhancedTelegramBot(config)
    
    print("✅ Bot initialized successfully!")
    print("🤖 Bot is now running...")
    print("📱 Send /start to your bot to test it!")
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())