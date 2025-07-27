#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask wrapper for Telegram Bot to run as Web Service on Render
"""

import os
import threading
import time
import logging
import sqlite3
from flask import Flask, jsonify, request
from bot import bot, logger as bot_logger, setup_authorized_users, device_manager, DB_FILE, SECURITY_CONFIG
from bot import command_executor as bot_command_executor

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعداد تسجيل خاص بـ Flask
flask_logger = logging.getLogger('flask_app')
flask_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
flask_logger.addHandler(handler)

# متغير لتتبع حالة البوت
bot_status = {
    "running": False,
    "start_time": None,
    "last_activity": None,
    "restart_count": 0,
    "active_devices": 0,
    "pending_commands": 0
}

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        "status": "running",
        "service": "Telegram Bot",
        "version": "2.1.7",
        "bot_running": bot_status["running"],
        "uptime": time.time() - bot_status["start_time"] if bot_status["start_time"] else 0,
        "security": SECURITY_CONFIG,
        "restarts": bot_status["restart_count"],
        "active_devices": bot_status["active_devices"],
        "pending_commands": bot_status["pending_commands"]
    })

@app.route('/health')
def health():
    """فحص صحة الخدمة"""
    try:
        # فحص اتصال قاعدة البيانات
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        
        # فحص اتصال خادم الأوامر
        if not bot_command_executor.check_connection():
            return jsonify({"status": "warning", "message": "Command server not connected"}), 200
            
        return jsonify({
            "status": "healthy",
            "bot_running": bot_status["running"],
            "db_connection": "ok",
            "command_server": "connected"
        })
    except Exception as e:
        flask_logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/status')
def status():
    """حالة البوت"""
    try:
        # حساب الأجهزة النشطة
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM devices WHERE status = "active"')
        active_devices = cursor.fetchone()[0]
        
        # حساب الأوامر المعلقة
        cursor.execute('SELECT COUNT(*) FROM commands WHERE status = "pending"')
        pending_commands = cursor.fetchone()[0]
        conn.close()
        
        bot_status["active_devices"] = active_devices
        bot_status["pending_commands"] = pending_commands
        
        return jsonify(bot_status)
    except Exception as e:
        flask_logger.error(f"Status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/restart', methods=['POST'])
def restart_bot():
    """إعادة تشغيل البوت"""
    try:
        # التحقق من التوقيع
        auth_token = request.headers.get('X-Auth-Token')
        if auth_token != os.environ.get('AUTH_TOKEN'):
            return jsonify({"error": "Unauthorized"}), 401
            
        flask_logger.info("Restarting bot...")
        global bot_thread
        if bot_thread.is_alive():
            bot.stop_polling()
            bot_thread.join(timeout=10)
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        return jsonify({"status": "restarting"})
    except Exception as e:
        flask_logger.error(f"Restart failed: {e}")
        return jsonify({"error": str(e)}), 500

def run_bot():
    """تشغيل البوت في خيط منفصل"""
    global bot_status
    try:
        # التحقق من وجود Token
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            bot_logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود في المتغيرات البيئية")
            return
        
        owner_id = os.environ.get('OWNER_USER_ID')
        if not owner_id:
            bot_logger.error("❌ OWNER_USER_ID غير موجود في المتغيرات البيئية")
            return
        
        bot_logger.info("🚀 بدء تشغيل بوت التحكم في الأجهزة...")
        bot_logger.info("✅ تم تهيئة النظام بنجاح")
        bot_logger.info("🔒 وضع الأمان مفعل")
        bot_logger.info("👻 وضع التخفي مفعل")
        bot_logger.info("💾 التخزين المحلي مفعل")
        bot_logger.info(f"🔑 Token موجود: {'نعم' if bot_token else 'لا'}")
        bot_logger.info(f"👤 معرف المالك: {owner_id}")
        
        bot_status["running"] = True
        bot_status["start_time"] = time.time()
        bot_status["restart_count"] += 1
        
        # إعداد المستخدمين المصرح لهم
        setup_authorized_users()
        
        # تشغيل البوت
        bot.polling(none_stop=True, interval=0, skip_pending=True)
        
    except Exception as e:
        bot_logger.error(f"خطأ في تشغيل البوت: {e}")
        bot_status["running"] = False
    finally:
        bot_status["running"] = False

def update_activity():
    """تحديث آخر نشاط"""
    while True:
        try:
            bot_status["last_activity"] = time.time()
            
            # تحديث إحصائيات الأجهزة
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM devices WHERE status = "active"')
            active_devices = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM commands WHERE status = "pending"')
            pending_commands = cursor.fetchone()[0]
            conn.close()
            
            bot_status["active_devices"] = active_devices
            bot_status["pending_commands"] = pending_commands
            
            time.sleep(60)  # تحديث كل دقيقة
        except Exception as e:
            flask_logger.error(f"Activity update failed: {e}")
            time.sleep(30)

# بدء تشغيل البوت عند التحميل
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# بدء تحديث النشاط
activity_thread = threading.Thread(target=update_activity, daemon=True)
activity_thread.start()

if __name__ == "__main__":
    # تشغيل Flask app
    port = int(os.environ.get('PORT', 10002))
    flask_logger.info(f"🌐 تشغيل Flask app على المنفذ: {port}")
    flask_logger.info(f"🔗 رابط الخدمة: https://remote-control-telegram-bot.onrender.com")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)