#!/usr/bin/env python3
"""
Simple Telegram Bot Runner
"""

import asyncio
import logging
from enhanced_telegram_bot import EnhancedTelegramBot, TelegramConfig

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def main():
    """Main function to run the bot"""
    print("🚀 Starting Enhanced Telegram Bot...")
    
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