#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask wrapper for Telegram Bot to run as Web Service on Render
"""

import os
import threading
import time
from flask import Flask, jsonify
from bot import bot, logger, setup_authorized_users

# إنشاء تطبيق Flask
app = Flask(__name__)

# متغير لتتبع حالة البوت
bot_status = {
    "running": False,
    "start_time": None,
    "last_activity": None
}

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        "status": "running",
        "service": "Telegram Bot",
        "bot_running": bot_status["running"],
        "uptime": time.time() - bot_status["start_time"] if bot_status["start_time"] else 0
    })

@app.route('/health')
def health():
    """فحص صحة الخدمة"""
    return jsonify({
        "status": "healthy",
        "bot_running": bot_status["running"]
    })

@app.route('/status')
def status():
    """حالة البوت"""
    return jsonify(bot_status)

def run_bot():
    """تشغيل البوت في خيط منفصل"""
    try:
        # التحقق من وجود Token
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود في المتغيرات البيئية")
            return
        
        owner_id = os.environ.get('OWNER_USER_ID')
        if not owner_id:
            logger.error("❌ OWNER_USER_ID غير موجود في المتغيرات البيئية")
            return
        
        logger.info("🚀 بدء تشغيل بوت التحكم في الأجهزة...")
        logger.info("✅ تم تهيئة النظام بنجاح")
        logger.info("🔒 وضع الأمان مفعل")
        logger.info("👻 وضع التخفي مفعل")
        logger.info("💾 التخزين المحلي مفعل")
        logger.info(f"🔑 Token موجود: {'نعم' if bot_token else 'لا'}")
        logger.info(f"👤 معرف المالك: {owner_id}")
        
        bot_status["running"] = True
        bot_status["start_time"] = time.time()
        
        # إعداد المستخدمين المصرح لهم
        setup_authorized_users()
        
        # تشغيل البوت
        bot.polling(none_stop=True, interval=0)
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        bot_status["running"] = False

def update_activity():
    """تحديث آخر نشاط"""
    while bot_status["running"]:
        bot_status["last_activity"] = time.time()
        time.sleep(60)  # تحديث كل دقيقة

if __name__ == "__main__":
    # بدء البوت في خيط منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # بدء تحديث النشاط في خيط منفصل
    activity_thread = threading.Thread(target=update_activity, daemon=True)
    activity_thread.start()
    
    # تشغيل Flask app
    port = int(os.environ.get('PORT', 10002))
    print(f"🌐 تشغيل Flask app على المنفذ: {port}")
    print(f"🔗 رابط الخدمة: https://remote-control-telegram-bot.onrender.com")
    app.run(host='0.0.0.0', port=port, debug=False)